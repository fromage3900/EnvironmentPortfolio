param(
    [ValidateSet('qwen3.8-27b', 'muse-glimmer-30b')]
    [string]$Model = 'qwen3.8-27b',
    [ValidateSet('4bit', 'bf16')]
    [string]$Precision = '4bit',
    [int]$Port = 8000
)

$pythonCommand = if ($env:LOCAL_HF_PYTHON) { $env:LOCAL_HF_PYTHON } else { 'python' }
$serverPath = Join-Path $PSScriptRoot 'local_hf_server.py'

& $pythonCommand $serverPath --model $Model --precision $Precision --port $Port
exit $LASTEXITCODE
