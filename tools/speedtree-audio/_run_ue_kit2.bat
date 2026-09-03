@echo off
"C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe" "C:/EnvironmentPortfolio/BS_GodFile/BS_GodFile.uproject" -run=PythonScript -script="C:/EnvironmentPortfolio/tools/speedtree-audio/build_seaabove_kit.py" -unattended -noP4 -nullRHI -NOSOUND -NoSplash -NoLiveCoding > "C:/EnvironmentPortfolio/tools/speedtree-audio/_ue_kit_run.log" 2>&1
