# package-msix.ps1 - Package app thành MSIX cho Microsoft Store
param(
    [Parameter(Mandatory=$false)]
    [string]$OutputName = "StarterAppLauncher.msix"
)

Write-Host "========================================"
Write-Host "Packaging App for Microsoft Store"
Write-Host "========================================"
Write-Host ""

# Kiểm tra file EXE
if (-not (Test-Path "dist\StarterAppLauncher.exe")) {
    Write-Error "❌ EXE file not found: dist\StarterAppLauncher.exe"
    Write-Host "Please run build.bat first to build the app."
    exit 1
}

# Tạo thư mục package
$packageDir = "msix-package"
if (Test-Path $packageDir) {
    Remove-Item $packageDir -Recurse -Force
}
New-Item -ItemType Directory -Path $packageDir | Out-Null

Write-Host "1. Copying EXE file..."
Copy-Item "dist\StarterAppLauncher.exe" "$packageDir\StarterAppLauncher.exe"

# Tạo thư mục Assets
Write-Host "2. Creating Assets directory..."
New-Item -ItemType Directory -Path "$packageDir\Assets" | Out-Null

# Copy hoặc tạo icons từ avatar.png
$avatarPath = "src\images\avatar.png"
if (Test-Path $avatarPath) {
    Write-Host "3. Creating icons from avatar.png..."
    
    # Sử dụng PowerShell để resize images (cần .NET)
    Add-Type -AssemblyName System.Drawing
    
    $img = [System.Drawing.Image]::FromFile((Resolve-Path $avatarPath))
    
    # StoreLogo.png - 50x50
    $storeLogo = New-Object System.Drawing.Bitmap(50, 50)
    $g = [System.Drawing.Graphics]::FromImage($storeLogo)
    $g.DrawImage($img, 0, 0, 50, 50)
    $storeLogo.Save("$packageDir\Assets\StoreLogo.png", [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $storeLogo.Dispose()
    
    # Square150x150Logo.png - 150x150
    $square150 = New-Object System.Drawing.Bitmap(150, 150)
    $g = [System.Drawing.Graphics]::FromImage($square150)
    $g.DrawImage($img, 0, 0, 150, 150)
    $square150.Save("$packageDir\Assets\Square150x150Logo.png", [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $square150.Dispose()
    
    # Square44x44Logo.png - 44x44
    $square44 = New-Object System.Drawing.Bitmap(44, 44)
    $g = [System.Drawing.Graphics]::FromImage($square44)
    $g.DrawImage($img, 0, 0, 44, 44)
    $square44.Save("$packageDir\Assets\Square44x44Logo.png", [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $square44.Dispose()
    
    # Wide310x150Logo.png - 310x150
    $wide310 = New-Object System.Drawing.Bitmap(310, 150)
    $g = [System.Drawing.Graphics]::FromImage($wide310)
    $g.DrawImage($img, 0, 0, 310, 150)
    $wide310.Save("$packageDir\Assets\Wide310x150Logo.png", [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $wide310.Dispose()
    
    # SplashScreen.png - 620x300
    $splash = New-Object System.Drawing.Bitmap(620, 300)
    $g = [System.Drawing.Graphics]::FromImage($splash)
    $g.DrawImage($img, 0, 0, 620, 300)
    $splash.Save("$packageDir\Assets\SplashScreen.png", [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $splash.Dispose()
    
    $img.Dispose()
    Write-Host "   ✅ Icons created"
} else {
    Write-Warning "⚠️  avatar.png not found. Please create icons manually in $packageDir\Assets\"
    Write-Host "   Required sizes:"
    Write-Host "   - StoreLogo.png: 50x50"
    Write-Host "   - Square150x150Logo.png: 150x150"
    Write-Host "   - Square44x44Logo.png: 44x44"
    Write-Host "   - Wide310x150Logo.png: 310x150"
    Write-Host "   - SplashScreen.png: 620x300"
}

# Copy AppxManifest.xml
Write-Host "4. Copying AppxManifest.xml..."
if (Test-Path "AppxManifest.xml") {
    Copy-Item "AppxManifest.xml" "$packageDir\AppxManifest.xml"
    Write-Host "   ✅ Manifest copied"
} else {
    Write-Error "❌ AppxManifest.xml not found!"
    exit 1
}

# Tìm MakeAppx.exe
Write-Host "5. Looking for MakeAppx.exe..."
$makeappx = $null
$kitPaths = @(
    "C:\Program Files (x86)\Windows Kits\10\bin",
    "C:\Program Files\Windows Kits\10\bin"
)

foreach ($kitPath in $kitPaths) {
    if (Test-Path $kitPath) {
        $kits = Get-ChildItem $kitPath -Directory -ErrorAction SilentlyContinue
        if ($kits) {
            $latestKit = $kits | Sort-Object Name -Descending | Select-Object -First 1
            $makeappxPath = Join-Path $latestKit.FullName "x64\makeappx.exe"
            if (Test-Path $makeappxPath) {
                $makeappx = $makeappxPath
                Write-Host "   ✅ Found: $makeappx"
                break
            }
        }
    }
}

if (-not $makeappx) {
    Write-Warning "⚠️  MakeAppx.exe not found!"
    Write-Host ""
    Write-Host "Please install Windows SDK:"
    Write-Host "https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/"
    Write-Host ""
    Write-Host "Or use MSIX Packaging Tool from Microsoft Store:"
    Write-Host "https://www.microsoft.com/store/productId/9N5LW3JBCXKF"
    Write-Host ""
    Write-Host "Package directory prepared at: $packageDir"
    Write-Host "You can manually package it using MSIX Packaging Tool GUI."
    exit 0
}

# Package MSIX
Write-Host "6. Packaging MSIX..."
$outputPath = Join-Path (Get-Location) $OutputName
& $makeappx pack /d $packageDir /p $outputPath /o

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================"
    Write-Host "✅ Package created successfully!"
    Write-Host "========================================"
    Write-Host "Output: $outputPath"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Sign the package (optional - Microsoft Store will sign it)"
    Write-Host "2. Upload to Microsoft Partner Center"
    Write-Host "3. Complete store listing"
    Write-Host "4. Submit for review"
    Write-Host ""
    Write-Host "See MICROSOFT_STORE_GUIDE.md for detailed instructions."
} else {
    Write-Error "❌ Packaging failed!"
    exit 1
}


