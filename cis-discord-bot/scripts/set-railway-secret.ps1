param(
    [string]$Name = "",
    [string]$Value = "",
    [string]$Service = "kira-bot",
    [string]$Environment = "production"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-SecretValue {
    param([string]$Prompt)

    $secureValue = Read-Host -Prompt $Prompt -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

if ([string]::IsNullOrWhiteSpace($Name)) {
    $Name = (Read-Host -Prompt "Variable name (e.g. BREVO_API_KEY)").Trim()
}

if ([string]::IsNullOrWhiteSpace($Name)) {
    throw "Variable name cannot be empty."
}

$secretValue = $Value
if ([string]::IsNullOrWhiteSpace($secretValue)) {
    $secretValue = Read-SecretValue -Prompt "Value for $Name (input hidden)"
}
else {
    Write-Warning "Value passed as parameter may be visible in shell history."
}

if ([string]::IsNullOrWhiteSpace($secretValue)) {
    throw "Variable value cannot be empty."
}

$railwayCmd = Get-Command railway -ErrorAction Stop
$cmdArgs = @(
    "variables", "set", "$Name=$secretValue",
    "--service", $Service,
    "--environment", $Environment
)

& $railwayCmd.Source @cmdArgs
if ($LASTEXITCODE -ne 0) {
    throw "Railway CLI command failed with exit code $LASTEXITCODE."
}

Write-Host "Updated Railway variable '$Name' for service '$Service' in environment '$Environment'."
