@echo off
chcp 65001 >nul
echo ============================================
echo  数通产品智能体 Android 应用初始化脚本
echo ============================================
echo.

cd /d "%~dp0"

echo [1/4] 检查 Node.js 环境...
where node >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js (https://nodejs.org)
    pause
    exit /b 1
)
node --version

echo.
echo [2/4] 安装项目依赖...
call npm install
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [3/4] 初始化 Capacitor 项目...
call npx cap init "数通产品智能体" com.localrest.mobile --web-dir=web
if errorlevel 1 (
    echo [警告] Capacitor 初始化可能已完成，请忽略此警告
)

echo.
echo [4/4] 添加 Android 平台...
call npx cap add android
if errorlevel 1 (
    echo [警告] Android 平台可能已添加，请忽略此警告
)

echo.
echo ============================================
echo  初始化完成！
echo ============================================
echo.
echo 下一步操作：
echo 1. 将 ../data/localrest.db 复制到 assets/ 目录下（命名为 localrest.db）
echo 2. 或者使用导入功能从 sampleData.json 加载示例数据
echo 3. 运行 `npx cap sync` 同步更改
echo 4. 运行 `npx cap open android` 打开 Android Studio 构建
echo 5. 或使用在线构建服务生成 APK
echo.
pause
