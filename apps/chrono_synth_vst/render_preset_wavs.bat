@echo off
setlocal
echo =========================================================
echo    CHRONO-DSP: Rendering Offline High-Quality WAVs
echo =========================================================
python "%~dp0chrono_dsp.py"
echo.
echo Check the '%~dp0renders' directory for generated audio files!
pause
endlocal
