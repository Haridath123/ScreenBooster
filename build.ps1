# ScreenBooster - Auto Builder (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ScreenBooster - Auto Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop any running instances
Write-Host "Stopping any running ScreenBooster instances..." -ForegroundColor Yellow
taskkill /f /im ScreenBooster.exe *> $null

# Clean up old builds
Write-Host "Cleaning old build files..." -ForegroundColor Yellow
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force release -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force debug_release -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Building RELEASE version..." -ForegroundColor Green
python -c "from build_exe import ScreenBoosterBuilder; builder = ScreenBoosterBuilder(); builder.run_build('release')" 2>&1

# Copy config files for release
Write-Host "Copying config files..." -ForegroundColor Yellow
Copy-Item "screenbooster_profiles.json" "dist\" -Force
Copy-Item "screenbooster_config.json" "dist\" -Force

# Create release package
Write-Host "Creating release package..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "release" | Out-Null
Copy-Item "dist\ScreenBooster.exe" "release\" -Force
Copy-Item "dist\screenbooster_profiles.json" "release\" -Force
Copy-Item "dist\screenbooster_config.json" "release\" -Force
Copy-Item "README.md" "release\" -Force
Copy-Item "BUILD_GUIDE.md" "release\" -Force

$releaseQuickStart = @"
# ScreenBooster - Quick Start

## Installation
1. Extract all files to a folder
2. Run ScreenBooster.exe
3. No installation required!

## Files Included
- ScreenBooster.exe - Main application
- screenbooster_profiles.json - Profile settings
- screenbooster_config.json - Configuration
- README.md - Complete documentation
- BUILD_GUIDE.md - Build instructions

Built: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Version: 2.3.0
"@
Set-Content -Path "release\QUICK_START.md" -Value $releaseQuickStart

Write-Host ""
Write-Host "Building DEBUG version..." -ForegroundColor Green
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue

python -c "from build_exe import ScreenBoosterBuilder; builder = ScreenBoosterBuilder(); builder.run_build('debug')" 2>&1

# Copy config files for debug
Copy-Item "screenbooster_profiles.json" "dist\" -Force
Copy-Item "screenbooster_config.json" "dist\" -Force

# Create debug release package
Write-Host "Creating debug release package..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "debug_release" | Out-Null
Copy-Item "dist\ScreenBooster.exe" "debug_release\" -Force
Copy-Item "dist\screenbooster_profiles.json" "debug_release\" -Force
Copy-Item "dist\screenbooster_config.json" "debug_release\" -Force
Copy-Item "README.md" "debug_release\" -Force

$debugQuickStart = @"
# ScreenBooster - Debug Version

## Installation
1. Extract all files to a folder
2. Run ScreenBooster.exe
3. Debug console window will be visible

## Debug Features
- Console window shows real-time output
- Error messages and debug information displayed
- All print statements visible in console

Built: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Version: 2.3.0 Debug
Mode: Console enabled
"@
Set-Content -Path "debug_release\QUICK_START_DEBUG.md" -Value $debugQuickStart

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           BUILD COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Release version: release\ScreenBooster.exe" -ForegroundColor White
Write-Host "Debug version:   debug_release\ScreenBooster.exe" -ForegroundColor White
Write-Host ""
Write-Host "Both versions are ready to run!" -ForegroundColor Green
Write-Host ""

# Ask if user wants to test
$test = Read-Host "Test release version now? (y/n)"
if ($test -eq "y") {
    Write-Host "Starting release version..." -ForegroundColor Yellow
    Set-Location release
    Start-Process ScreenBooster.exe
    Set-Location ..
}

$test2 = Read-Host "Test debug version now? (y/n)"
if ($test2 -eq "y") {
    Write-Host "Starting debug version..." -ForegroundColor Yellow
    Set-Location debug_release
    Start-Process ScreenBooster.exe
    Set-Location ..
}

Write-Host ""
Write-Host "Build process completed!" -ForegroundColor Green
Read-Host "Press Enter to exit"
