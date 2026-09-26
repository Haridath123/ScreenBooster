# ScreenBooster v2.0 - Executable Build Guide

## Building the Executable

### Method 1: Using the Build Script (Recommended)
1. Run `build.bat` - This will automatically install dependencies and build the exe

### Method 2: Manual Build
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Build the executable:
   ```bash
   python setup.py build
   ```

## Output Location
The executable will be created in:
```
build\exe.win-amd64-3.12\ScreenBooster.exe
```

## Creating a Portable Version
To distribute the program:
1. Copy the entire `build\exe.win-amd64-3.12` folder
2. Rename it to `ScreenBooster`
3. The folder contains all necessary DLLs and dependencies
4. Users can run `ScreenBooster.exe` directly

## Alternative: PyInstaller (If cx_Freeze has issues)

### Install PyInstaller
```bash
pip install pyinstaller
```

### Build with PyInstaller
```bash
pyinstaller --onefile --windowed --name ScreenBooster main.py
```

### PyInstaller Options
- `--onefile`: Creates a single exe file (larger but simpler)
- `--windowed`: No console window (remove if you want console)
- `--name`: Sets the output filename

## Notes
- The executable may be flagged by antivirus software (false positive)
- First run might be slower as it extracts dependencies
- Keyboard controls work the same in the executable
- Settings file (`screenbooster_settings.json`) will be created in the same folder as the exe

## Troubleshooting
- If build fails, try running as Administrator
- Ensure all dependencies are installed
- For Windows Defender issues, add the exe to exceptions
