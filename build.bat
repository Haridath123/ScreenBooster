@echo off
echo Building ScreenBooster as single EXE...
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
pyinstaller --onefile --console --name=ScreenBooster --add-data="screenbooster_settings.json;." --hidden-import=numpy --hidden-import=PIL --hidden-import=keyboard --hidden-import=ctypes --hidden-import=wmi --collect-all=numpy --collect-all=PIL main.py

echo.
if exist "dist\ScreenBooster.exe" (
    echo ✅ Build successful!
    echo 📦 EXE created: dist\ScreenBooster.exe
    
    REM Show file size
    for %%I in ("dist\ScreenBooster.exe") do echo 📏 Size: %%~zI bytes
    
    echo.
    echo 🎉 Ready for distribution!
    echo 📄 Copy ScreenBooster.exe to any computer and run it
    echo 📁 Settings files will be created automatically
    echo 💡 Console window will be visible for menu input
) else (
    echo ❌ Build failed!
)

echo.
pause
