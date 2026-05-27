package com.localrest.mobile

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import org.json.JSONArray
import java.io.InputStream

class DatabaseHelper(context: Context) : SQLiteOpenHelper(context, DATABASE_NAME, null, DATABASE_VERSION) {

    companion object {
        private const val DATABASE_NAME = "localrest.db"
        private const val DATABASE_VERSION = 1

        private const val TABLE_PRODUCTS = "products"
        private const val COLUMN_ID = "id"
        private const val COLUMN_CODE = "code"
        private const val COLUMN_NAME = "name"
        private const val COLUMN_BRAND = "brand"
        private const val COLUMN_CATEGORY = "category"
        private const val COLUMN_SPEC = "spec"
        private const val COLUMN_DESCRIPTION = "description"
    }

    override fun onCreate(db: SQLiteDatabase) {
        val createTable = """
            CREATE TABLE IF NOT EXISTS $TABLE_PRODUCTS (
                $COLUMN_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                $COLUMN_CODE TEXT,
                $COLUMN_NAME TEXT,
                $COLUMN_BRAND TEXT,
                $COLUMN_CATEGORY TEXT,
                $COLUMN_SPEC TEXT,
                $COLUMN_DESCRIPTION TEXT
            )
        """.trimIndent()
        db.execSQL(createTable)
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS $TABLE_PRODUCTS")
        onCreate(db)
    }

    fun importFromJson(inputStream: InputStream) {
        val jsonString = inputStream.bufferedReader().use { it.readText() }
        val jsonArray = JSONArray(jsonString)
        
        val db = writableDatabase
        db.beginTransaction()
        
        try {
            for (i in 0 until jsonArray.length()) {
                val product = jsonArray.getJSONObject(i)
                val code = product.optString("code", "")
                val name = product.optString("name", "")
                val brand = product.optString("brand", "")
                val category = product.optString("category", "")
                val spec = product.optString("spec", "")
                val description = product.optString("description", "")

                val insertSql = """
                    INSERT INTO $TABLE_PRODUCTS ($COLUMN_CODE, $COLUMN_NAME, $COLUMN_BRAND, $COLUMN_CATEGORY, $COLUMN_SPEC, $COLUMN_DESCRIPTION)
                    VALUES (?, ?, ?, ?, ?, ?)
                """.trimIndent()

                db.execSQL(insertSql, arrayOf(code, name, brand, category, spec, description))
            }
            db.setTransactionSuccessful()
        } finally {
            db.endTransaction()
        }
    }

    fun getAllProducts(): String {
        val db = readableDatabase
        val cursor = db.rawQuery("SELECT * FROM $TABLE_PRODUCTS", null)
        val products = mutableListOf<Map<String, String>>()
        
        while (cursor.moveToNext()) {
            val product = mutableMapOf<String, String>()
            for (i in 0 until cursor.columnCount) {
                product[cursor.getColumnName(i)] = cursor.getString(i) ?: ""
            }
            products.add(product)
        }
        cursor.close()
        
        return productsToJson(products)
    }

    fun getProductByCode(code: String): String {
        val db = readableDatabase
        val cursor = db.rawQuery("SELECT * FROM $TABLE_PRODUCTS WHERE $COLUMN_CODE = ?", arrayOf(code))
        
        if (cursor.moveToFirst()) {
            val product = mutableMapOf<String, String>()
            for (i in 0 until cursor.columnCount) {
                product[cursor.getColumnName(i)] = cursor.getString(i) ?: ""
            }
            cursor.close()
            return productToJson(product)
        }
        cursor.close()
        return "{}"
    }

    fun getProductsByBrand(brand: String): String {
        val db = readableDatabase
        val cursor = db.rawQuery("SELECT * FROM $TABLE_PRODUCTS WHERE $COLUMN_BRAND = ?", arrayOf(brand))
        val products = mutableListOf<Map<String, String>>()
        
        while (cursor.moveToNext()) {
            val product = mutableMapOf<String, String>()
            for (i in 0 until cursor.columnCount) {
                product[cursor.getColumnName(i)] = cursor.getString(i) ?: ""
            }
            products.add(product)
        }
        cursor.close()
        
        return productsToJson(products)
    }

    private fun productToJson(product: Map<String, String>): String {
        val sb = StringBuilder()
        sb.append("{")
        product.entries.forEachIndexed { index, entry ->
            if (index > 0) sb.append(",")
            sb.append("\"${entry.key}\":\"${escapeJson(entry.value)}\"")
        }
        sb.append("}")
        return sb.toString()
    }

    private fun productsToJson(products: List<Map<String, String>>): String {
        val sb = StringBuilder()
        sb.append("[")
        products.forEachIndexed { index, product ->
            if (index > 0) sb.append(",")
            sb.append(productToJson(product))
        }
        sb.append("]")
        return sb.toString()
    }

    private fun escapeJson(value: String): String {
        return value.replace("\\", "\\\\")
                    .replace("\"", "\\\"")
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t")
    }
}
