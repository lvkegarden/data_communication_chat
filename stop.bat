@echo off
title Stop Spring Boot Service
echo ==============================================
echo        Stop Spring Boot Service
echo ==============================================
echo.

echo Finding process on port 8080...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    echo Stopping process %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo Finding process on port 5001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001') do (
    echo Stopping process %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo Stopping all Java processes...
taskkill /F /IM java.exe >nul 2>&1

echo Stopping all Python processes...
taskkill /F /IM python.exe >nul 2>&1

echo.
echo Service stopped
echo ==============================================
pause