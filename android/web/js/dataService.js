(function(window) {
    'use strict';

    const DATA_SOURCE_MODE = {
        AUTO: 'auto',
        LOCAL: 'local',
        REMOTE: 'remote'
    };

    let currentMode = DATA_SOURCE_MODE.LOCAL;
    let dbConnection = null;
    let remoteApiBase = 'http://localhost:8080/api';
    let llmApiBase = 'http://localhost:5001/api';

    const DataService = {
        init: async function(options = {}) {
            currentMode = options.mode || DATA_SOURCE_MODE.LOCAL;
            if (options.remoteApiBase) {
                remoteApiBase = options.remoteApiBase;
            }
            if (options.llmApiBase) {
                llmApiBase = options.llmApiBase;
            }

            if (currentMode === DATA_SOURCE_MODE.LOCAL) {
                try {
                    await this.initSqlite();
                } catch (e) {
                    console.warn('SQLite 初始化失败，切换到 JSON 数据源:', e);
                    currentMode = 'json';
                }
            }

            return currentMode;
        },

        initSqlite: async function() {
            if (typeof Capacitor === 'undefined' || !Capacitor.Plugins || !Capacitor.Plugins.SQLite) {
                throw new Error('Capacitor SQLite 插件不可用');
            }

            const { SQLite } = Capacitor.Plugins;
            const result = await SQLite.checkConnectionsConsistency();
            if (!result.result) {
                await SQLite.initWebStore();
            }

            dbConnection = await SQLite.createConnection({
                database: 'localrest.db',
                encrypted: false,
                mode: 'no-encryption',
                version: 1
            });

            await dbConnection.open();

            await this.ensureTables();
        },

        ensureTables: async function() {
            const createTableSQL = `
                CREATE TABLE IF NOT EXISTS product_specs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_code TEXT UNIQUE NOT NULL,
                    product_name TEXT,
                    series TEXT,
                    product_url TEXT,
                    source TEXT,
                    category TEXT,
                    status TEXT,
                    description TEXT,
                    thumbnail_url TEXT,
                    specs_json TEXT,
                    links_json TEXT,
                    raw_data TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
            `;
            await dbConnection.execute({ statements: createTableSQL });
        },

        isNetworkAvailable: async function() {
            if (typeof Capacitor === 'undefined' || !Capacitor.Plugins || !Capacitor.Plugins.Network) {
                return false;
            }
            const { Network } = Capacitor.Plugins;
            const status = await Network.getStatus();
            return status.connected;
        },

        getProducts: async function(options = {}) {
            if (currentMode === DATA_SOURCE_MODE.REMOTE || 
                (currentMode === DATA_SOURCE_MODE.AUTO && await this.isNetworkAvailable())) {
                return this.getProductsRemote(options);
            }
            return this.getProductsLocal(options);
        },

        getProductsLocal: async function(options = {}) {
            const { keyword = '', category = '', source = '', limit = 100, offset = 0 } = options;
            
            let sql = 'SELECT id, product_code, product_name, series, source, category, description FROM product_specs WHERE 1=1';
            const params = [];

            if (keyword) {
                sql += ' AND (product_code LIKE ? OR product_name LIKE ? OR series LIKE ? OR description LIKE ?)';
                const kw = `%${keyword}%`;
                params.push(kw, kw, kw, kw);
            }
            if (category) {
                sql += ' AND category = ?';
                params.push(category);
            }
            if (source) {
                sql += ' AND source = ?';
                params.push(source);
            }
            sql += ' ORDER BY id DESC LIMIT ? OFFSET ?';
            params.push(limit, offset);

            const result = await dbConnection.query({ statement: sql, values: params });
            
            return {
                success: true,
                products: result.values || [],
                count: (result.values || []).length,
                source: 'local'
            };
        },

        getProductsRemote: async function(options = {}) {
            const { keyword = '', category = '', source = '' } = options;
            let url = `${remoteApiBase}/product-data/search?`;
            
            if (keyword) url += `keyword=${encodeURIComponent(keyword)}&`;
            if (category) url += `category=${encodeURIComponent(category)}&`;
            if (source) url += `source=${encodeURIComponent(source)}&`;

            const response = await fetch(url);
            const data = await response.json();
            return { ...data, source: 'remote' };
        },

        getProductDetail: async function(productCode) {
            if (currentMode === DATA_SOURCE_MODE.REMOTE || 
                (currentMode === DATA_SOURCE_MODE.AUTO && await this.isNetworkAvailable())) {
                return this.getProductDetailRemote(productCode);
            }
            return this.getProductDetailLocal(productCode);
        },

        getProductDetailLocal: async function(productCode) {
            const sql = 'SELECT * FROM product_specs WHERE product_code = ?';
            const result = await dbConnection.query({ statement: sql, values: [productCode] });
            
            if (result.values && result.values.length > 0) {
                const product = result.values[0];
                if (product.specs_json) {
                    try {
                        product.specs = JSON.parse(product.specs_json);
                    } catch (e) {
                        product.specs = {};
                    }
                }
                if (product.links_json) {
                    try {
                        product.links = JSON.parse(product.links_json);
                    } catch (e) {
                        product.links = {};
                    }
                }
                return { success: true, product, source: 'local' };
            }
            return { success: false, error: '产品不存在', source: 'local' };
        },

        getProductDetailRemote: async function(productCode) {
            const response = await fetch(`${remoteApiBase}/product-data/detail/${encodeURIComponent(productCode)}`);
            const data = await response.json();
            return { ...data, source: 'remote' };
        },

        getCompetitors: async function(productCode, limit = 3) {
            if (currentMode === DATA_SOURCE_MODE.REMOTE || 
                (currentMode === DATA_SOURCE_MODE.AUTO && await this.isNetworkAvailable())) {
                return this.getCompetitorsRemote(productCode, limit);
            }
            return this.getCompetitorsLocal(productCode, limit);
        },

        getCompetitorsLocal: async function(productCode, limit = 3) {
            const sql = `
                SELECT * FROM product_specs 
                WHERE id != (SELECT id FROM product_specs WHERE product_code = ?)
                ORDER BY RANDOM() 
                LIMIT ?
            `;
            const result = await dbConnection.query({ statement: sql, values: [productCode, limit] });
            return {
                success: true,
                competitors: result.values || [],
                count: (result.values || []).length,
                source: 'local'
            };
        },

        getCompetitorsRemote: async function(productCode, limit = 3) {
            const response = await fetch(
                `${remoteApiBase}/product-data/competitors/${encodeURIComponent(productCode)}?limit=${limit}`
            );
            const data = await response.json();
            return { ...data, source: 'remote' };
        },

        callLLM: async function(message, sessionId = 'mobile_session') {
            const isOnline = await this.isNetworkAvailable();
            
            if (!isOnline) {
                return {
                    success: false,
                    error: '当前网络不可用，大模型调用需要网络连接',
                    source: 'offline'
                };
            }

            try {
                const response = await fetch(`${llmApiBase}/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        message: message,
                        flag: 'y'
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP 错误: ${response.status}`);
                }
                
                const data = await response.json();
                return { ...data, source: 'remote' };
            } catch (e) {
                return {
                    success: false,
                    error: '大模型调用失败: ' + e.message,
                    source: 'error'
                };
            }
        },

        importDataFromJson: async function(products) {
            if (!dbConnection) {
                throw new Error('数据库未初始化');
            }

            const insertSQL = `
                INSERT OR REPLACE INTO product_specs 
                (product_code, product_name, series, product_url, source, category, status, 
                 description, thumbnail_url, specs_json, links_json, raw_data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `;

            for (const p of products) {
                await dbConnection.query({
                    statement: insertSQL,
                    values: [
                        p.product_code || p.productCode,
                        p.product_name || p.productName,
                        p.series,
                        p.product_url || p.productUrl,
                        p.source,
                        p.category,
                        p.status,
                        p.description,
                        p.thumbnail_url || p.thumbnailUrl,
                        p.specs_json || (p.specs ? JSON.stringify(p.specs) : null),
                        p.links_json || (p.links ? JSON.stringify(p.links) : null),
                        p.raw_data || (p.rawData ? JSON.stringify(p.rawData) : null),
                        p.created_at || new Date().toISOString(),
                        p.updated_at || new Date().toISOString()
                    ]
                });
            }

            return { success: true, imported: products.length };
        },

        getDataSourceMode: function() {
            return currentMode;
        },

        setDataSourceMode: function(mode) {
            currentMode = mode;
        }
    };

    window.DataService = DataService;
})(window);
