@echo off
echo ========================================
echo    ScreenBooster - Auto Builder
echo ========================================
echo.

:: Stop any running instances
echo Stopping any running ScreenBooster instances...
taskkill /f /im ScreenBooster.exe >nul 2>&1

:: Clean up old builds
echo Cleaning old build files...
rmdir /s /q dist >nul 2>&1
rmdir /s /q build >nul 2>&1
rmdir /s /q release >nul 2>&1
rmdir /s /q debug_release >nul 2>&1

echo.
echo Building RELEASE version...
python -c "from build_exe import ScreenBoosterBuilder; builder = ScreenBoosterBuilder(); builder.run_build('release')" 2>&1

:: Copy config files for release
echo Copying config files...
copy "screenbooster_profiles.json" "dist\" >nul 2>&1
copy "screenbooster_config.json" "dist\" >nul 2>&1

:: Create release package
echo Creating release package...
mkdir release >nul 2>&1
copy "dist\ScreenBooster.exe" "release\" >nul 2>&1
copy "dist\screenbooster_profiles.json" "release\" >nul 2>&1
copy "dist\screenbooster_config.json" "release\" >nul 2>&1
copy "README.md" "release\" >nul 2>&1
copy "BUILD_GUIDE.md" "release\" >nul 2>&1

echo # ScreenBooster - Quick Start > "release\QUICK_START.md"
echo. >> "release\QUICK_START.md"
echo ## Installation >> "release\QUICK_START.md"
echo 1. Extract all files to a folder >> "release\QUICK_START.md"
echo 2. Run ScreenBooster.exe >> "release\QUICK_START.md"
echo 3. No installation required! >> "release\QUICK_START.md"
echo. >> "release\QUICK_START.md"
echo Built: %date% %time% >> "release\QUICK_START.md"
echo Version: 2.2.0 >> "release\QUICK_START.md"

echo.
echo Building DEBUG version...
rmdir /s /q dist >nul 2>&1
rmdir /s /q build >nul 2>&1

python -c "from build_exe import ScreenBoosterBuilder; builder = ScreenBoosterBuilder(); builder.run_build('debug')" 2>&1

:: Copy config files for debug
copy "screenbooster_profiles.json" "dist\" >nul 2>&1
copy "screenbooster_config.json" "dist\" >nul 2>&1

:: Create debug release package
echo Creating debug release package...
mkdir debug_release >nul 2>&1
copy "dist\ScreenBooster.exe" "debug_release\" >nul 2>&1
copy "dist\screenbooster_profiles.json" "debug_release\" >nul 2>&1
copy "dist\screenbooster_config.json" "debug_release\" >nul 2>&1
copy "README.md" "debug_release\" >nul 2>&1

echo # ScreenBooster - Debug Version > "debug_release\QUICK_START_DEBUG.md"
echo. >> "debug_release\QUICK_START_DEBUG.md"
echo ## Installation >> "debug_release\QUICK_START_DEBUG.md"
echo 1. Extract all files to a folder >> "debug_release\QUICK_START_DEBUG.md"
echo 2. Run ScreenBooster.exe >> "debug_release\QUICK_START_DEBUG.md"
echo 3. Debug console window will be visible >> "debug_release\QUICK_START_DEBUG.md"
echo. >> "debug_release\QUICK_START_DEBUG.md"
echo Built: %date% %time% >> "debug_release\QUICK_START_DEBUG.md"
echo Version: 2.2.0 Debug >> "debug_release\QUICK_START_DEBUG.md"

echo.
echo ========================================
echo           BUILD COMPLETE!
echo ========================================
echo.
echo Release version: release\ScreenBooster.exe
echo Debug version:   debug_release\ScreenBooster.exe
echo.
echo Both versions are ready to run!
echo.

:: Ask if user wants to test
set /p test="Test release version now? (y/n): "
if /i "%test%"=="y" (
    echo Starting release version...
    cd release
    start ScreenBooster.exe
    cd ..
)

set /p test2="Test debug version now? (y/n): "
if /i "%test2%"=="y" (
    echo Starting debug version...
    cd debug_release
    start ScreenBooster.exe
    cd ..
)

echo.
echo Build process completed!
pause
