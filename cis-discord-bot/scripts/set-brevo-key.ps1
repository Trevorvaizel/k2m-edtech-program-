param(
    [string]$EnvPath = "",
    [string]$ApiKey = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-EnvPath {
    param(
        [string]$ScriptDirectory,
        [string]$CurrentEnvPath
    )

    $botDir = Split-Path -Parent $ScriptDirectory
    if ([string]::IsNullOrWhiteSpace($CurrentEnvPath)) {
        return Join-Path $botDir ".env"
    }

    if ([System.IO.Path]::IsPathRooted($CurrentEnvPath)) {
        return $CurrentEnvPath
    }

    return Join-Path $botDir $CurrentEnvPath
}

function Ensure-EnvFile {
    param(
        [string]$TargetEnvPath,
        [string]$ScriptDirectory
    )

    if (Test-Path $TargetEnvPath) {
        return
    }

    $botDir = Split-Path -Parent $ScriptDirectory
    $templatePath = Join-Path $botDir ".env.template"

    if (Test-Path $templatePath) {
        Copy-Item -Path $templatePath -Destination $TargetEnvPath
        Write-Host "Created $TargetEnvPath from .env.template"
        return
    }

    New-Item -ItemType File -Path $TargetEnvPath -Force | Out-Null
    Write-Host "Created empty env file at $TargetEnvPath"
}

function Read-SecretFromPrompt {
    $secureValue = Read-Host -Prompt "Paste your Brevo API key (input hidden)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)

    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

function Upsert-BrevoApiKey {
    param(
        [string]$TargetEnvPath,
        [string]$Value
    )

    $raw = ""
    if (Test-Path $TargetEnvPath) {
        $raw = Get-Content -Path $TargetEnvPath -Raw
    }

    $lines = @()
    if (-not [string]::IsNullOrEmpty($raw)) {
        $normalized = $raw -replace "`r`n", "`n"
        $lines = $normalized -split "`n", -1
        if ($lines.Count -gt 0 -and $lines[-1] -eq "") {
            $lines = $lines[0..($lines.Count - 2)]
        }
    }

    $updatedLines = New-Object System.Collections.Generic.List[string]
    $replaced = $false

    foreach ($line in $lines) {
        if ($line -match "^BREVO_API_KEY=") {
            if (-not $replaced) {
                $updatedLines.Add("BREVO_API_KEY=$Value")
                $replaced = $true
            }
            continue
        }

        $updatedLines.Add($line)
    }

    if (-not $replaced) {
        if ($updatedLines.Count -gt 0 -and $updatedLines[$updatedLines.Count - 1] -ne "") {
            $updatedLines.Add("")
        }
        $updatedLines.Add("BREVO_API_KEY=$Value")
    }

    $content = ($updatedLines.ToArray() -join "`r`n")
    if (-not $content.EndsWith("`r`n")) {
        $content += "`r`n"
    }

    Set-Content -Path $TargetEnvPath -Value $content -NoNewline -Encoding Ascii
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$resolvedEnvPath = Resolve-EnvPath -ScriptDirectory $scriptDir -CurrentEnvPath $EnvPath

Ensure-EnvFile -TargetEnvPath $resolvedEnvPath -ScriptDirectory $scriptDir

$keyValue = $ApiKey
if ([string]::IsNullOrWhiteSpace($keyValue)) {
    $keyValue = Read-SecretFromPrompt
}
else {
    Write-Warning "ApiKey was passed as a parameter. This may be visible in shell history."
}

if ([string]::IsNullOrWhiteSpace($keyValue)) {
    throw "BREVO_API_KEY cannot be empty."
}

$backupPath = "$resolvedEnvPath.bak.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item -Path $resolvedEnvPath -Destination $backupPath -Force

Upsert-BrevoApiKey -TargetEnvPath $resolvedEnvPath -Value $keyValue

Write-Host "BREVO_API_KEY updated in $resolvedEnvPath"
Write-Host "Backup written to $backupPath"
