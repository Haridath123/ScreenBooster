# ScreenBooster V4 - EXE Build Guide

## 🎯 Introduction to Building Executables

This guide explains how to build ScreenBooster V4 into a standalone executable (.exe) file that can be distributed and run without Python installation. We'll cover both the manual build process and an automated one-click solution.

## 📋 Prerequisites for Building

### **Required Software:**
1. **Python 3.8+** - Installed and added to PATH
2. **ScreenBooster V4 Source Code** - Complete project folder
3. **Command Prompt/PowerShell** - For running build commands

### **Required Python Packages:**
```bash
pip install pyinstaller pillow numpy keyboard
```

## 🔧 Manual Build Process

### **Step 1: Install PyInstaller**
```bash
pip install pyinstaller
```

### **Step 2: Navigate to Project Directory**
```bash
cd C:\Users\YourName\Desktop\Data\ScreenBooster\ScreenBoosterV4
```

### **Step 3: Basic Build Command**
```bash
pyinstaller --onefile --windowed main.py
```

### **Step 4: Advanced Build with Customization**
```bash
pyinstaller --onefile --windowed --name ScreenBoosterV4 --distpath dist --workpath build ScreenBoosterV4.spec
```

### **Step 5: Copy Configuration Files**
```bash
copy screenbooster_profiles.json dist\
copy screenbooster_config.json dist\
```

## 📁 Understanding Build Artifacts

### **Generated Files and Folders:**
- **build/** - Temporary build files (can be deleted)
- **dist/** - Contains the final .exe file
- **ScreenBoosterV4.spec** - PyInstaller configuration file
- **__pycache__/** - Python cache files (can be deleted)

### **Final Output:**
```
dist/
├── ScreenBoosterV4.exe           # Main executable
├── screenbooster_profiles.json   # Profile settings
└── screenbooster_config.json     # Configuration
```

## ⚙️ PyInstaller Options Explained

### **Common Options:**
- `--onefile` - Create single .exe file
- `--windowed` - Hide console window (for GUI apps)
- `--console` - Show console window (for debugging)
- `--name NAME` - Set executable name
- `--distpath PATH` - Set output directory
- `--workpath PATH` - Set build directory

### **Advanced Options:**
- `--icon ICON.ico` - Add custom icon
- `--add-data "SOURCE;DEST"` - Include additional files
- `--hidden-import MODULE` - Include hidden dependencies
- `--exclude-module MODULE` - Exclude specific modules

## 🎨 Custom .spec File Configuration

### **Default spec file contents:**
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=['numpy', 'PIL', 'keyboard'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ScreenBoosterV4',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          windowed=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None)
```

### **Enhanced spec file with data files:**
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[
                 ('screenbooster_profiles.json', '.'),
                 ('screenbooster_config.json', '.')
             ],
             hiddenimports=['numpy', 'PIL', 'keyboard'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ScreenBoosterV4',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          windowed=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='icon.ico')  # Optional: Add custom icon
```

## 🐛 Common Build Issues & Solutions

### **1. Module Not Found Errors**
**Problem:** `ModuleNotFoundError: No module named 'X'`
**Solution:** Add to hiddenimports in .spec file:
```python
hiddenimports=['numpy', 'PIL', 'keyboard', 'missing_module']
```

### **2. Large File Size**
**Problem:** EXE file is too large (>100MB)
**Solutions:**
- Exclude unnecessary modules:
  ```python
  excludes=['tkinter', 'unittest', 'test']
  ```
- Use UPX compression (enabled by default)
- Remove debug information

### **3. EXE Crashes on Startup**
**Problem:** EXE closes immediately without error
**Solutions:**
- Build with `--console` flag to see error messages
- Check for missing data files
- Verify all dependencies are included

### **4. Permission Denied Errors**
**Problem:** Can't save configuration files
**Solution:** Ensure JSON files are copied to dist folder and use absolute paths

### **5. Antivirus False Positives**
**Problem:** Antivirus flags the EXE as malicious
**Solutions:**
- Add exclusion to antivirus
- Code sign the EXE (if available)
- Use reputable PyInstaller version

## 🚀 Optimization Techniques

### **Reduce File Size:**
```python
# In .spec file
excludes=[
    'tkinter', 'unittest', 'test', 'pdb', 'doctest',
    'pydoc', 'xml', 'email', 'http', 'urllib', 'ssl'
]
```

### **Improve Startup Time:**
```python
# In .spec file
a = Analysis(['main.py'],
             # ... other options
             noarchive=False)  # Set to True for faster startup
```

### **Include Custom Icon:**
```bash
# Create icon.ico (256x256) and add to build
pyinstaller --onefile --windowed --icon icon.ico main.py
```

## 📦 Distribution Preparation

### **Pre-Distribution Checklist:**
1. ✅ Test the built EXE on clean system
2. ✅ Verify all JSON files are included
3. ✅ Check file permissions work correctly
4. ✅ Test safety lock and keyboard controls
5. ✅ Verify profile switching functionality
6. ✅ Test on different Windows versions

### **Creating Distribution Package:**
```bash
# Create distribution folder
mkdir ScreenBoosterV4_Release
copy dist\ScreenBoosterV4.exe ScreenBoosterV4_Release\
copy screenbooster_profiles.json ScreenBoosterV4_Release\
copy screenbooster_config.json ScreenBoosterV4_Release\
copy README.md ScreenBoosterV4_Release\
copy EXTREME_CUSTOMIZATION.md ScreenBoosterV4_Release\
```

### **Version Numbering:**
- Update version in README.md
- Create release notes
- Tag release in version control

## 🔧 Advanced Build Options

### **Multi-Version Build:**
```bash
# Build different versions
pyinstaller --onefile --windowed --name ScreenBoosterV4_Debug --console main.py
pyinstaller --onefile --windowed --name ScreenBoosterV4_Release main.py
```

### **Automated Testing:**
```python
# test_build.py - Simple test script
import subprocess
import os
import sys

def test_exe():
    exe_path = "dist/ScreenBoosterV4.exe"
    if os.path.exists(exe_path):
        print("✅ EXE exists")
        # Add more tests here
    else:
        print("❌ EXE not found")
        sys.exit(1)

if __name__ == "__main__":
    test_exe()
```

### **Build Script Integration:**
```python
# build.py - Advanced build script
import subprocess
import shutil
import os

def clean_build():
    """Clean previous build artifacts"""
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")

def build_exe():
    """Build the executable"""
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "ScreenBoosterV4",
        "main.py"
    ]
    subprocess.run(cmd, check=True)

def copy_configs():
    """Copy configuration files"""
    os.makedirs("dist", exist_ok=True)
    shutil.copy("screenbooster_profiles.json", "dist/")
    shutil.copy("screenbooster_config.json", "dist/")

if __name__ == "__main__":
    clean_build()
    build_exe()
    copy_configs()
    print("✅ Build complete!")
```

## 📋 Build Command Reference

### **Basic Commands:**
```bash
# Simple build
pyinstaller main.py

# Single file build
pyinstaller --onefile main.py

# Windowed build (no console)
pyinstaller --onefile --windowed main.py

# Custom name and output
pyinstaller --onefile --windowed --name MyApp --distpath output main.py
```

### **Advanced Commands:**
```bash
# With custom icon
pyinstaller --onefile --windowed --icon app.ico main.py

# With data files
pyinstaller --onefile --windowed --add-data "data.json;." main.py

# With hidden imports
pyinstaller --onefile --windowed --hidden-import "module_name" main.py

# Using spec file
pyinstaller ScreenBoosterV4.spec
```

## 🎯 Best Practices

### **Before Building:**
1. Update all dependencies
2. Test the Python script thoroughly
3. Clean up unnecessary files
4. Update documentation

### **During Build:**
1. Use virtual environment
2. Build in clean directory
3. Monitor for warnings
4. Test intermediate steps

### **After Building:**
1. Test on multiple systems
2. Check file size and performance
3. Verify all features work
4. Create proper documentation

### **Distribution:**
1. Include all necessary files
2. Provide clear installation instructions
3. Test installation process
4. Create proper versioning

---

## 🔚 Conclusion

Building ScreenBooster V4 into an executable is straightforward with PyInstaller. The key is understanding the build options, handling dependencies correctly, and testing thoroughly before distribution.

The automated build script (build_exe.py) provided in this repository makes the process as simple as running a single Python file, ensuring consistent builds every time.

**Happy building!** 🚀
