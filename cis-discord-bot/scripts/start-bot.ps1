param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$botDir = Split-Path -Parent $scriptDir
$logDir = Join-Path $botDir "logs"
$pidFile = Join-Path $logDir "bot-autostart.pid"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

$statusLog = Join-Path $logDir "bot-autostart-status.log"

function Write-Status {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $statusLog -Value "[$ts] $Message"
}

try {
    $pythonExe = if ($env:K2M_BOT_PYTHON) { $env:K2M_BOT_PYTHON } else { "python" }

    $running = $null
    if (Test-Path $pidFile) {
        $savedPidRaw = (Get-Content -Raw $pidFile).Trim()
        $savedPid = 0
        if ([int]::TryParse($savedPidRaw, [ref]$savedPid) -and $savedPid -gt 0) {
            $byPid = Get-CimInstance Win32_Process -Filter "ProcessId = $savedPid" -ErrorAction SilentlyContinue
            if ($byPid -and $byPid.Name -like "python*") {
                $running = @($byPid)
            }
        }
    }

    if (-not $running) {
        $running = Get-CimInstance Win32_Process |
            Where-Object {
                $_.Name -like "python*" -and
                $_.CommandLine -match "main\\.py"
            }
    }

    if ($running) {
        $firstPid = [int]$running[0].ProcessId
        Set-Content -Path $pidFile -Value $firstPid
        Write-Status "Bot already running. PID=$firstPid"
        exit 0
    }

    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $stdoutLog = Join-Path $logDir "bot-autostart-$stamp.out.log"
    $stderrLog = Join-Path $logDir "bot-autostart-$stamp.err.log"

    $proc = Start-Process `
        -FilePath $pythonExe `
        -ArgumentList "main.py" `
        -WorkingDirectory $botDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutLog `
        -RedirectStandardError $stderrLog `
        -PassThru

    Set-Content -Path $pidFile -Value $proc.Id
    Write-Status "Started bot PID=$($proc.Id) using '$pythonExe'"
}
catch {
    Write-Status "Auto-start failed: $($_.Exception.Message)"
    throw
}
