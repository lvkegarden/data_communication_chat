@echo off
setlocal
title Spring Boot Local REST Service

echo ==============================================
echo       Spring Boot Local REST Service
echo ==============================================
echo.

echo Checking environment...

where mvn >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Maven not found in PATH
    echo Please install Maven and add it to system PATH
    pause
    exit /b 1
)
echo [OK] Maven found

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH
    echo Please install Python and add it to system PATH
    pause
    exit /b 1
)
echo [OK] Python found

echo.
echo Stopping existing services on port 8080 and 5001...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    echo Stopping process %%a on port 8080...
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001 ^| findstr LISTENING') do (
    echo Stopping process %%a on port 5001...
    taskkill /F /PID %%a >nul 2>&1
)

echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo.
echo [1/2] Starting Python service (port 5001)...

cd /d "%~dp0python"
start "Python Service - Port 5001" cmd /c "python app.py & echo. & echo Python Service Stopped & pause"

echo Python service starting in new window...
echo Waiting 5 seconds for Python service to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Starting Spring Boot service (port 8080)...

cd /d "%~dp0"
start "Spring Boot Service - Port 8080" cmd /c "mvn spring-boot:run & echo. & echo Spring Boot Service Stopped & pause"

echo Spring Boot service starting in new window...
echo Waiting 10 seconds for Spring Boot service to initialize...
timeout /t 10 /nobreak >nul

echo.
echo ==============================================
echo  Services started:
echo   - Python: http://localhost:5001
echo   - Spring Boot: http://localhost:8080
echo ==============================================
echo.
echo Both services are running in separate windows.
echo Close the windows to stop the services.
echo.
pause
