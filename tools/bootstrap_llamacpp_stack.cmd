@echo off
REM Bootstrap: wait for llama-cpp-python build, start local OpenAI server on Qwen GGUF, run daemon once.
set LOGDIR=c:\EnvironmentPortfolio\logs\overnight
if not exist %LOGDIR% mkdir %LOGDIR%

:waitbuild
if not exist c:\EnvironmentPortfolio\.venv-llamacpp\Lib\site-packages\llama_cpp (
  timeout /t 30 /nobreak >nul
  goto waitbuild
)
echo [%time%] llama_cpp installed >> %LOGDIR%\bootstrap.log

set GGUF=F:\OllamaModels\blobs\sha256-1194192cf2a187eb02722edcc3f77b11d21f537048ce04b67ccf8ba78863006a
start /b "" c:\EnvironmentPortfolio\.venv-llamacpp\Scripts\python.exe -m llama_cpp.server --model %GGUF% --host 127.0.0.1 --port 8081 --n_ctx 8192 --n_threads 8 > %LOGDIR%\llamaserver.log 2>&1

REM wait for server health
:waitserver
timeout /t 15 /nobreak >nul
curl.exe -s -o nul -w "%%{http_code}" http://127.0.0.1:8081/health | findstr 200 >nul
if errorlevel 1 goto waitserver
echo [%time%] llama server up on 8081 >> %LOGDIR%\bootstrap.log

set OLLAMA_CHAT_URL=http://127.0.0.1:8081/v1/chat/completions
set QWEN_MODEL=qwen3-coder-30b
python c:\EnvironmentPortfolio\scripts\overnight_daemon.py --lanes health,content,research,git,forums,playhouse --once >> %LOGDIR%\first_run.log 2>&1
echo [%time%] daemon pass complete >> %LOGDIR%\bootstrap.log
