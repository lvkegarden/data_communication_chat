package com.localrest.mobile

import android.content.Context
import android.webkit.JavascriptInterface
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

class ApiBridge(private val context: Context, private val databaseHelper: DatabaseHelper) {

    private val LLM_API_URL = "http://localhost:5001/api/chat"
    private val LLM_API_URL_ALT = "http://10.0.2.2:5001/api/chat"

    @JavascriptInterface
    fun ping(): String {
        return "{\"status\": \"ok\", \"message\": \"ApiBridge is working\"}"
    }

    @JavascriptInterface
    fun getAllProducts(): String {
        return try {
            databaseHelper.getAllProducts()
        } catch (e: Exception) {
            "{\"error\": \"${e.message}\"}"
        }
    }

    @JavascriptInterface
    fun getProductByCode(code: String): String {
        return try {
            databaseHelper.getProductByCode(code)
        } catch (e: Exception) {
            "{\"error\": \"${e.message}\"}"
        }
    }

    @JavascriptInterface
    fun getProductsByBrand(brand: String): String {
        return try {
            databaseHelper.getProductsByBrand(brand)
        } catch (e: Exception) {
            "{\"error\": \"${e.message}\"}"
        }
    }

    @JavascriptInterface
    fun callLLM(message: String): String {
        return try {
            val result = makeHttpPost(LLM_API_URL, message)
            if (result.contains("error") && result.contains("Connection")) {
                return makeHttpPost(LLM_API_URL_ALT, message)
            }
            result
        } catch (e: Exception) {
            "{\"error\": \"${e.message}\"}"
        }
    }

    @JavascriptInterface
    fun callLLMWithProduct(code: String, question: String): String {
        val productJson = databaseHelper.getProductByCode(code)
        if (productJson == "{}") {
            return "{\"error\": \"Product not found\"}"
        }
        
        val prompt = "基于以下产品信息回答问题：\n\n产品信息：$productJson\n\n问题：$question"
        return callLLM(prompt)
    }

    @JavascriptInterface
    fun searchProducts(keyword: String): String {
        return try {
            val allProducts = databaseHelper.getAllProducts()
            if (keyword.isBlank()) {
                return allProducts
            }
            
            val lowerKeyword = keyword.lowercase()
            val filtered = mutableListOf<String>()
            val pattern = """\{[^}]*\}""".toRegex()
            
            pattern.findAll(allProducts).forEach { match ->
                val product = match.value
                if (product.lowercase().contains(lowerKeyword)) {
                    filtered.add(product)
                }
            }
            
            return "[${filtered.joinToString(",")}]"
        } catch (e: Exception) {
            "{\"error\": \"${e.message}\"}"
        }
    }

    private fun makeHttpPost(urlString: String, message: String): String {
        val url = URL(urlString)
        val connection = url.openConnection() as HttpURLConnection
        
        return try {
            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.setRequestProperty("Accept", "application/json")
            connection.connectTimeout = 10000
            connection.readTimeout = 30000
            connection.doOutput = true

            val jsonBody = "{\"message\": \"${escapeJson(message)}\"}"
            val outputStream: OutputStream = connection.outputStream
            outputStream.write(jsonBody.toByteArray())
            outputStream.flush()
            outputStream.close()

            val responseCode = connection.responseCode
            val reader = if (responseCode == HttpURLConnection.HTTP_OK) {
                BufferedReader(InputStreamReader(connection.inputStream))
            } else {
                BufferedReader(InputStreamReader(connection.errorStream))
            }

            val response = StringBuilder()
            var line: String?
            while (reader.readLine().also { line = it } != null) {
                response.append(line)
            }
            reader.close()

            response.toString()
        } catch (e: Exception) {
            "{\"error\": \"HTTP Error: ${e.message}\"}"
        } finally {
            connection.disconnect()
        }
    }

    private fun escapeJson(value: String): String {
        return value.replace("\\", "\\\\")
                    .replace("\"", "\\\"")
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t")
    }
}
