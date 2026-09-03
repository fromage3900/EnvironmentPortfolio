# Waits for an installed Ollama worker model (granite4.2:3b or granite4.2:8b),
# then runs the daemon's first full live pass autonomously. The previous waiter
# targeted qwen3-coder:30b, which does not fit on a 12 GB GPU and hung the loop.
$python = if ($env:LOCAL_HF_PYTHON) { $env:LOCAL_HF_PYTHON } else { 'python' }
$workdir = 'C:\EnvironmentPortfolio'
Set-Location $workdir
$deadline = (Get-Date).AddMinutes(45)
$targetModels = @('granite4.2:3b', 'granite4.2:8b', 'muse-glimmer:30b')

while ((Get-Date) -lt $deadline) {
    $list = & ollama list 2>$null | Out-String
    $found = $targetModels | Where-Object { $list -match [regex]::Escape($_) } | Select-Object -First 1
    if ($found) {
        "[$((Get-Date).ToString('HH:mm:ss'))] found model $found; starting daemon" | Add-Content logs\overnight\first_run.log
        & $python scripts\overnight_daemon.py --once *>> logs\overnight\first_run.log
        exit $LASTEXITCODE
    }
    Start-Sleep -Seconds 60
}

"[$((Get-Date).ToString('HH:mm:ss'))] ERROR: no worker model available after 45 minutes" | Add-Content logs\overnight\first_run.log
exit 1
