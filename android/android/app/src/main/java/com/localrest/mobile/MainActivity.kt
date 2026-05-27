package com.localrest.mobile

import android.annotation.SuppressLint
import android.content.Context
import android.os.Bundle
import android.webkit.*
import androidx.appcompat.app.AppCompatActivity
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var databaseHelper: DatabaseHelper

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        databaseHelper = DatabaseHelper(this)
        copyDatabaseIfNeeded()

        webView = findViewById(R.id.webView)
        setupWebView()
        loadLocalHtml()
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.setSupportZoom(false)
        settings.cacheMode = WebSettings.LOAD_NO_CACHE

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                return false
            }
        }

        webView.webChromeClient = WebChromeClient()

        webView.addJavascriptInterface(ApiBridge(this, databaseHelper), "ApiBridge")
    }

    private fun loadLocalHtml() {
        webView.loadUrl("file:///android_asset/web/index.html")
    }

    private fun copyDatabaseIfNeeded() {
        val dbPath = getDatabasePath("localrest.db").path
        val dbFile = File(dbPath)
        
        if (!dbFile.exists()) {
            try {
                val assets = assets
                var inputStream: InputStream? = null
                
                try {
                    inputStream = assets.open("localrest.db")
                } catch (e: Exception) {
                    try {
                        inputStream = assets.open("sampleData.json")
                        databaseHelper.importFromJson(inputStream!!)
                        return
                    } catch (e2: Exception) {
                        return
                    }
                }
                
                dbFile.parentFile?.mkdirs()
                val outputStream = FileOutputStream(dbFile)
                inputStream?.copyTo(outputStream)
                outputStream.close()
                inputStream?.close()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
