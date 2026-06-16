# Local Web dashboard (reads DB config from project root .env)
$ErrorActionPreference = "Stop"
$DevDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $DevDir
$ReqFile = Join-Path $DevDir "requirements-dashboard.txt"
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"

function Get-DashboardPort {
    param([string]$EnvPath)
    $port = 8080
    if (Test-Path $EnvPath) {
        Get-Content $EnvPath -Encoding UTF8 | ForEach-Object {
            if ($_ -match '^\s*WEB_DASHBOARD_PORT\s*=\s*"?(\d+)"?\s*$') {
                $script:port = [int]$Matches[1]
            }
        }
    }
    return $port
}

function Stop-ListenPort {
    param([int]$Port)
    $killed = $false
    netstat -ano | Select-String ":\s*$Port\s+.*LISTENING" | ForEach-Object {
        $procId = ($_.Line.Trim() -split '\s+')[-1]
        if ($procId -match '^\d+$' -and [int]$procId -gt 0) {
            Write-Host "[INFO] Port $Port in use by PID $procId, stopping..." -ForegroundColor Yellow
            Stop-Process -Id ([int]$procId) -Force -ErrorAction SilentlyContinue
            $killed = $true
        }
    }
    if ($killed) { Start-Sleep -Milliseconds 500 }
}

if (-not (Test-Path (Join-Path $Root ".env"))) {
    Write-Host "[hint] No .env found. Copy example.env: copy example.env .env" -ForegroundColor Yellow
}

$Port = Get-DashboardPort -EnvPath (Join-Path $Root ".env")
Stop-ListenPort -Port $Port

if (Test-Path $VenvPython) {
    $Python = $VenvPython
} else {
    $Python = "python"
}

& $Python -c "import fastapi" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Installing dashboard deps: $ReqFile" -ForegroundColor Cyan
    & $Python -m pip install -r $ReqFile
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[error] pip install failed" -ForegroundColor Red
        exit 1
    }
}

Set-Location (Join-Path $Root "scripts")
$env:PYTHONUNBUFFERED = "1"

# Windows PowerShell 下 & 启动的子进程有时收不到 Ctrl+C，显式转发终止信号
$proc = Start-Process -FilePath $Python -ArgumentList @("-u", "run_dashboard.py") `
    -WorkingDirectory (Get-Location) -PassThru -NoNewWindow
if (-not $proc) {
    Write-Host "[error] failed to start dashboard" -ForegroundColor Red
    exit 1
}

$cancelHandler = [ConsoleCancelEventHandler]{
    param($sender, $e)
    $e.Cancel = $true
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}
[Console]::Add_CancelKeyPress($cancelHandler) | Out-Null
try {
    $proc.WaitForExit()
    if ($proc.ExitCode -ne 0) { exit $proc.ExitCode }
} finally {
    [Console]::Remove_CancelKeyPress($cancelHandler) | Out-Null
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}
