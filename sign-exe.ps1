# sign-exe.ps1 - Script để ký số file EXE
param(
    [Parameter(Mandatory=$true)]
    [string]$ExePath,
    
    [Parameter(Mandatory=$false)]
    [string]$CertPath = "code-signing-cert.pfx",
    
    [Parameter(Mandatory=$false)]
    [string]$Password = "YourPassword123!"
)

# Tìm signtool.exe
$signtool = $null
$kitPaths = @(
    "C:\Program Files (x86)\Windows Kits\10\bin",
    "C:\Program Files\Windows Kits\10\bin"
)

foreach ($kitPath in $kitPaths) {
    if (Test-Path $kitPath) {
        $kits = Get-ChildItem $kitPath -Directory -ErrorAction SilentlyContinue
        if ($kits) {
            $latestKit = $kits | Sort-Object Name -Descending | Select-Object -First 1
            $signtoolPath = Join-Path $latestKit.FullName "x64\signtool.exe"
            if (Test-Path $signtoolPath) {
                $signtool = $signtoolPath
                Write-Host "Found signtool: $signtool"
                break
            }
        }
    }
}

if (-not $signtool) {
    Write-Error "❌ signtool.exe not found! Please install Windows SDK."
    Write-Host "Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/"
    exit 1
}

if (-not (Test-Path $ExePath)) {
    Write-Error "❌ EXE file not found: $ExePath"
    exit 1
}

if (-not (Test-Path $CertPath)) {
    Write-Error "❌ Certificate file not found: $CertPath"
    Write-Host "Create a certificate first using:"
    Write-Host '  $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=StarterAppLauncher" -CertStoreLocation "Cert:\CurrentUser\My"'
    Write-Host '  $password = ConvertTo-SecureString -String "YourPassword123!" -Force -AsPlainText'
    Write-Host '  Export-PfxCertificate -Cert $cert -FilePath "code-signing-cert.pfx" -Password $password'
    exit 1
}

Write-Host "========================================"
Write-Host "Signing EXE file..."
Write-Host "========================================"
Write-Host "EXE: $ExePath"
Write-Host "Certificate: $CertPath"
Write-Host ""

# Ký số
& $signtool sign `
    /f $CertPath `
    /p $Password `
    /fd SHA256 `
    /td SHA256 `
    /tr http://timestamp.digicert.com `
    /a `
    $ExePath

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ File signed successfully!"
    Write-Host ""
    
    # Verify
    Write-Host "Verifying signature..."
    & $signtool verify /pa /v $ExePath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Signature verified!"
        Write-Host ""
        Write-Host "You can check the signature in file properties (Digital Signatures tab)."
    } else {
        Write-Warning "⚠ Signature verification failed!"
    }
} else {
    Write-Error "❌ Signing failed!"
    exit 1
}

