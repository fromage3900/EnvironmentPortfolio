# Registers Windows Scheduled Tasks for the Melodia Overnight Daemon.
# Run from an elevated PowerShell to register both tasks.
param(
    [switch]$HealthOnly
)

$python = if ($env:LOCAL_HF_PYTHON) { $env:LOCAL_HF_PYTHON } else { 'python' }
$daemon = Join-Path $PSScriptRoot '..\scripts\overnight_daemon.py'
$workdir = Split-Path $PSScriptRoot -Parent
$action  = New-ScheduledTaskAction -Execute $python -Argument "`"$daemon`"" -WorkingDirectory $workdir

# 1) Full overnight run: all lanes, every night at 23:00
$nightTrigger = New-ScheduledTaskTrigger -Daily -At '23:00'
Register-ScheduledTask -TaskName 'Melodia Overnight Daemon' `
    -Action $action -Trigger $nightTrigger `
    -Description 'Melodia autonomous overnight lanes (content/research/git/forums/playhouse/health)' `
    -Force

# 2) Health check lane: every 15 minutes, always on
$healthArgs    = "`"$daemon`" --health-only"
$healthAction  = New-ScheduledTaskAction -Execute $python -Argument $healthArgs -WorkingDirectory $workdir
$healthTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName 'Melodia Health Check' `
    -Action $healthAction -Trigger $healthTrigger `
    -Description '24/7 autonomous health checks: Ollama, model smoke test, HF server, TD MCP, disk, repo state' `
    -Force

Get-ScheduledTask -TaskName 'Melodia Overnight Daemon', 'Melodia Health Check' | Select-Object TaskName, State
Write-Host "Registered. Start the night run manually with: Start-ScheduledTask -TaskName 'Melodia Overnight Daemon'"
