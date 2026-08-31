@echo off
REM Auto-detect hython.exe and print its path (also used by other scripts via call)
setlocal enabledelayedexpansion
set "HOUDINI_ROOT=C:\Program Files\Side Effects Software"
if not exist "%HOUDINI_ROOT%" (
  echo hython NOT FOUND: no Houdini install under "%HOUDINI_ROOT%"
  exit /b 1
)
set "LATEST="
for /f "delims=" %%D in ('dir /b /ad /o-n "%HOUDINI_ROOT%\Houdini*"') do (
  if not defined LATEST if exist "%HOUDINI_ROOT%\%%D\bin\hython.exe" set "LATEST=%HOUDINI_ROOT%\%%D\bin\hython.exe"
)
if defined LATEST (
  echo !LATEST!
  exit /b 0
)
echo hython NOT FOUND in any Houdini version directory
exit /b 1
