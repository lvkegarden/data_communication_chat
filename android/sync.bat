@echo off
chcp 65001 >nul
echo ============================================
echo  同步 Capacitor 项目
echo ============================================
echo.

cd /d "%~dp0"

echo 正在同步更改...
call npx cap sync

echo.
echo 同步完成！
echo 如果需要打开 Android Studio，请运行: npx cap open android
echo.
pause
