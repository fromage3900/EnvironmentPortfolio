@echo off
REM SpeedTree -> Houdini -> UE staging for one kit asset.
REM Usage: run_speedtree_bridge.cmd <path\to\Asset.stmat> [res]
call "%~dp0..\houdini_hython\where_hython.cmd" > "%TEMP%\hython_path.txt" 2>nul
set /p HYTHON=<"%TEMP%\hython_path.txt"
if not defined HYTHON ( echo hython NOT FOUND & exit /b 1 )
"%HYTHON%" "%~dp0speedtree_bridge.py" --stmat "%~1" --res %2
