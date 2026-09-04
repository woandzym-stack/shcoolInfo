@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 检查 8081 端口...

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8081" ^| findstr "LISTENING"') do (
    echo 发现 8081 端口被 PID %%P 占用，正在清理...
    taskkill /PID %%P /T /F >nul 2>&1
)

timeout /t 1 /nobreak >nul

echo 启动 Uvicorn...
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8081