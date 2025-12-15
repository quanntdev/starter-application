# create-cert.ps1 - Tạo self-signed certificate để ký số
param(
    [Parameter(Mandatory=$false)]
    [string]$Subject = "CN=StarterAppLauncher",
    
    [Parameter(Mandatory=$false)]
    [string]$FriendlyName = "Starter App Launcher Code Signing",
    
    [Parameter(Mandatory=$false)]
    [string]$Password = "YourPassword123!",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "code-signing-cert.pfx"
)

Write-Host "========================================"
Write-Host "Creating Code Signing Certificate..."
Write-Host "========================================"
Write-Host ""

# Tạo certificate
try {
    $cert = New-SelfSignedCertificate `
        -Type CodeSigningCert `
        -Subject $Subject `
        -KeyUsage DigitalSignature `
        -FriendlyName $FriendlyName `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
    
    Write-Host "✅ Certificate created successfully!"
    Write-Host "   Thumbprint: $($cert.Thumbprint)"
    Write-Host "   Subject: $($cert.Subject)"
    Write-Host ""
    
    # Export to PFX
    $securePassword = ConvertTo-SecureString -String $Password -Force -AsPlainText
    Export-PfxCertificate `
        -Cert $cert `
        -FilePath $OutputFile `
        -Password $securePassword `
        -ErrorAction Stop
    
    Write-Host "✅ Certificate exported to: $OutputFile"
    Write-Host ""
    Write-Host "========================================"
    Write-Host "Next steps:"
    Write-Host "========================================"
    Write-Host "1. Use this certificate to sign your EXE:"
    Write-Host "   .\sign-exe.ps1 -ExePath `"dist\StarterAppLauncher.exe`""
    Write-Host ""
    Write-Host "2. Or it will be used automatically when running build.bat"
    Write-Host ""
    Write-Host "⚠️  Note: Self-signed certificates are for testing only."
    Write-Host "   Windows will still show 'Unknown publisher' warning."
    Write-Host "   For production, purchase a certificate from a CA."
    Write-Host ""
    
} catch {
    Write-Error "❌ Failed to create certificate: $_"
    exit 1
}


