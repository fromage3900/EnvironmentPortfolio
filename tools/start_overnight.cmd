@echo off
REM One-launch overnight starter for Windows. Ensures Ollama is reachable, pulls the
REM recommended fleet, and runs the daemon once.
setlocal enabledelayedexpansion
set WORKDIR=C:\EnvironmentPortfolio
if not exist %WORKDIR%\logs\overnight mkdir %WORKDIR%\logs\overnight

set PYTHON=python
if defined LOCAL_HF_PYTHON set PYTHON=%LOCAL_HF_PYTHON%

cd /d %WORKDIR%

REM Probe Ollama API for up to 5 minutes.
set /a attempts=0
:probe
curl.exe -s -o nul -w "%%{http_code}" http://127.0.0.1:11434/api/tags | findstr 200 >nul
if errorlevel 1 (
    set /a attempts+=1
    if %attempts% gtr 30 (
        echo [%time%] ERROR: Ollama not reachable after 5 minutes >> logs\overnight\start_overnight.log
        exit /b 1
    )
    timeout /t 10 /nobreak >nul
    goto probe
)
echo [%time%] Ollama reachable >> logs\overnight\start_overnight.log

REM Pull fleet (best-effort).
%PYTHON% tools\pull_fleet.py >> logs\overnight\start_overnight.log 2>&1

REM Run daemon once.
%PYTHON% scripts\overnight_daemon.py --lanes health,content,research,git,forums,playhouse --once >> logs\overnight\start_overnight.log 2>&1
set DAEMON_RC=%errorlevel%
echo [%time%] daemon finished rc=%DAEMON_RC% >> logs\overnight\start_overnight.log
exit /b %DAEMON_RC%
