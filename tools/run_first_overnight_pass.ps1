# Waits for the qwen3-coder:30b pull to finish, then runs the daemon's first
# full live pass autonomously. Launched detached by the setup session.
$python = if ($env:LOCAL_HF_PYTHON) { $env:LOCAL_HF_PYTHON } else { 'python' }
$workdir = 'C:\EnvironmentPortfolio'
Set-Location $workdir
$deadline = (Get-Date).AddMinutes(45)
while ((Get-Date) -lt $deadline) {
    $list = & ollama list 2>$null | Out-String
    if ($list -match 'qwen3-coder:30b') {
        & $python scripts\overnight_daemon.py --once *>> logs\overnight\first_run.log
        exit $LASTEXITCODE
    }
    Start-Sleep -Seconds 60
}
exit 1
