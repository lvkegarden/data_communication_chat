@echo off
chcp 65001 >nul
echo ============================================
echo  导出 Keystore 为 Base64
echo ============================================
echo.

set KEYSTORE_FILE=localrest-release.keystore
set OUTPUT_FILE=keystore-base64.txt

if not exist %KEYSTORE_FILE% (
    echo [错误] 未找到 %KEYSTORE_FILE%
    echo 请先运行 generate-keystore.bat 生成证书
    pause
    exit /b 1
)

echo 正在转换为 Base64...
certutil -encode %KEYSTORE_FILE% %OUTPUT_FILE%

echo.
echo ============================================
echo  转换完成！
echo ============================================
echo.
echo 输出文件: %OUTPUT_FILE%
echo.
echo 请打开 %OUTPUT_FILE%，复制所有内容（去掉首尾的 -----BEGIN CERTIFICATE----- 和 -----END CERTIFICATE-----）
echo 然后粘贴到 GitHub Secrets 的 KEYSTORE_FILE 中
echo.
pause
