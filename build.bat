@echo off
echo Building ScreenBoosterV2 as single EXE...
echo.

REM Install required packages including PyInstaller
echo Installing packages...
pip install -r requirements.txt
pip install pyinstaller

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Cleaned previous builds...

REM Build the executable as single file WITH CONSOLE (fixes input() issue)
echo Building single EXE with console support...
pyinstaller --onefile --console --name=ScreenBoosterV2 --add-data="screenbooster_settings.json;." --hidden-import=numpy --hidden-import=PIL --hidden-import=keyboard --hidden-import=ctypes --hidden-import=wmi --collect-all=numpy --collect-all=PIL main.py

echo.
if exist "dist\ScreenBoosterV2.exe" (
    echo ✅ Build successful!
    echo 📦 EXE created: dist\ScreenBoosterV2.exe
    
    REM Show file size
    for %%I in ("dist\ScreenBoosterV2.exe") do echo 📏 Size: %%~zI bytes
    
    echo.
    echo 🎉 Ready for distribution!
    echo 📄 Copy ScreenBoosterV2.exe to any computer and run it
    echo 📁 Settings files will be created automatically
    echo 💡 Console window will be visible for menu input
) else (
    echo ❌ Build failed!
)

echo.
pause
