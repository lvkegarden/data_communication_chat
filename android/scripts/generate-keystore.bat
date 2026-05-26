@echo off
chcp 65001 >nul
echo ============================================
echo  生成 Android 签名证书 (Keystore)
echo ============================================
echo.

set KEYSTORE_NAME=localrest-release.keystore
set KEYSTORE_PASSWORD=localrest123
set KEY_ALIAS=localrest
set KEY_PASSWORD=localrest123
set DNAME="CN=LocalRest, OU=LocalRest, O=LocalRest, L=Local, ST=Local, C=CN"
set VALIDITY=10000

echo 正在生成签名证书...
echo.

where keytool >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 keytool，请确保已安装 Java JDK
    pause
    exit /b 1
)

keytool -genkeypair ^
    -v ^
    -keystore %KEYSTORE_NAME% ^
    -alias %KEY_ALIAS% ^
    -keyalg RSA ^
    -keysize 2048 ^
    -validity %VALIDITY% ^
    -storepass %KEYSTORE_PASSWORD% ^
    -keypass %KEY_PASSWORD% ^
    -dname %DNAME%

if errorlevel 1 (
    echo.
    echo [错误] 证书生成失败
    pause
    exit /b 1
)

echo.
echo ============================================
echo  证书生成成功！
echo ============================================
echo.
echo 证书文件名: %KEYSTORE_NAME%
echo 别名 (Alias): %KEY_ALIAS%
echo Keystore 密码: %KEYSTORE_PASSWORD%
echo Key 密码: %KEY_PASSWORD%
echo.
echo 下一步：
echo 1. 将 %KEYSTORE_NAME% 转换为 Base64
echo 2. 在 GitHub Secrets 中配置以下变量：
echo    - KEYSTORE_FILE: keystore 的 Base64 内容
echo    - KEYSTORE_PASSWORD: %KEYSTORE_PASSWORD%
echo    - KEY_ALIAS: %KEY_ALIAS%
echo    - KEY_PASSWORD: %KEY_PASSWORD%
echo.
echo 转换 Base64 命令：
echo certutil -encode %KEYSTORE_NAME% keystore-base64.txt
echo.
pause
