@echo off
REM Bootstrap: ensure the recommended Ollama fleet is present, verify Ollama is
REM reachable, then run the overnight daemon once. Replaces the old llama-cpp-python
REM path, which used a hardcoded GGUF blob and the non-Ollama model name.
setlocal enabledelayedexpansion
set LOGDIR=c:\EnvironmentPortfolio\logs\overnight
if not exist %LOGDIR% mkdir %LOGDIR%

echo [%time%] bootstrap started >> %LOGDIR%\bootstrap.log

REM 1. Verify Ollama is on PATH and the API is reachable.
:waitollama
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [%time%] Ollama not on PATH; waiting... >> %LOGDIR%\bootstrap.log
    timeout /t 30 /nobreak >nul
    goto waitollama
)

curl.exe -s -o nul -w "%%{http_code}" http://127.0.0.1:11434/api/tags | findstr 200 >nul
if errorlevel 1 (
    echo [%time%] Ollama API not reachable; waiting... >> %LOGDIR%\bootstrap.log
    timeout /t 15 /nobreak >nul
    goto waitollama
)
echo [%time%] Ollama reachable >> %LOGDIR%\bootstrap.log

REM 2. Pull the recommended fleet (skips already-present models).
python c:\EnvironmentPortfolio\tools\pull_fleet.py >> %LOGDIR%\bootstrap.log 2>&1
if errorlevel 1 (
    echo [%time%] fleet pull reported failures; continuing with installed models >> %LOGDIR%\bootstrap.log
)

REM 3. Run the daemon once with the new worker/reasoner tier defaults.
python c:\EnvironmentPortfolio\scripts\overnight_daemon.py --lanes health,content,research,git,forums,playhouse --once >> %LOGDIR%\first_run.log 2>&1
set DAEMON_RC=%errorlevel%
echo [%time%] daemon pass complete rc=%DAEMON_RC% >> %LOGDIR%\bootstrap.log
exit /b %DAEMON_RC%
