// ============================================================================
// 前端 Web 配置文件
// 路径: config/web-config.js
// ============================================================================
// 使用说明:
// 1. 此文件包含所有前端页面的 API 地址配置
// 2. 在 HTML 页面中引入此文件后，可以通过 window.AppConfig 访问配置
// 3. 修改此文件后刷新页面即可生效，无需重新编译
// 4. 如果部署到不同环境时，只需修改此文件中的地址
// ============================================================================

(function(window) {
    'use strict';

    const AppConfig = {
        api: {
            javaBaseUrl: 'http://localhost:8080/api',
            pythonBaseUrl: 'http://localhost:5001/api'
        },
        endpoints: {
            chat: '/chat/chat',
            collect: '/collect',
            productData: '/product-data'
        }
    };

    window.AppConfig = AppConfig;
})(window);
