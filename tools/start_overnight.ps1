#!/usr/bin/env pwsh
# One-launch overnight starter for Windows. Ensures Ollama is reachable, pulls the
# recommended fleet, and runs the daemon once.
param(
    [string]$Workdir = 'C:\EnvironmentPortfolio',
    [string]$Lanes = 'health,content,research,git,forums,playhouse',
    [switch]$Once = $true
)

$python = if ($env:LOCAL_HF_PYTHON) { $env:LOCAL_HF_PYTHON } else { 'python' }
Set-Location $Workdir

New-Item -ItemType Directory -Force -Path 'logs\overnight' | Out-Null

# Probe Ollama API for up to 5 minutes.
$deadline = (Get-Date).AddMinutes(5)
while ((Get-Date) -lt $deadline) {
    try {
        $r = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 5 -ErrorAction Stop
        "[$((Get-Date).ToString('HH:mm:ss'))] Ollama reachable ($($r.models.Count) models)" | Add-Content 'logs\overnight\start_overnight.log'
        break
    } catch {
        Start-Sleep -Seconds 10
    }
}

# Pull fleet (best-effort).
& $python tools\pull_fleet.py *>> 'logs\overnight\start_overnight.log'

$flag = if ($Once) { '--once' } else { '' }
& $python scripts\overnight_daemon.py --lanes $Lanes $flag *>> 'logs\overnight\start_overnight.log'
exit $LASTEXITCODE
