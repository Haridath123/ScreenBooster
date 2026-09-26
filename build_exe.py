#!/usr/bin/env python3
"""
Build ScreenBooster as a single self-contained EXE using PyInstaller
"""

import os
import sys
import subprocess
import shutil

def build_exe():
    """Build ScreenBooster as a single EXE"""
    
    print("🔨 Building ScreenBooster EXE...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean previous builds
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🧹 Cleaned {folder} folder")
    
    # PyInstaller command for single EXE
    cmd = [
        "pyinstaller",
        "--onefile",                    # Create single EXE
        "--windowed",                   # Hide console window (remove if you want console)
        "--name=ScreenBoosterV2",      # EXE name
        "--icon=icon.ico",              # Icon file (optional)
        "--add-data=screenbooster_settings.json;.",  # Include settings file
        "--hidden-import=numpy",        # Ensure numpy is included
        "--hidden-import=PIL",          # Ensure PIL is included
        "--hidden-import=keyboard",     # Ensure keyboard is included
        "--hidden-import=ctypes",       # Ensure ctypes is included
        "--hidden-import=wmi",          # Ensure wmi is included
        "--collect-all=numpy",          # Collect all numpy dependencies
        "--collect-all=PIL",            # Collect all PIL dependencies
        "main.py"                       # Main script
    ]
    
    # Remove icon option if icon file doesn't exist
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
        print("⚠️  icon.ico not found, building without icon")
    
    print("🚀 Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        
        # Check if EXE was created
        exe_path = os.path.join("dist", "ScreenBoosterV2.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📦 EXE created: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
            
            # Create a simple README for distribution
            readme_content = """# ScreenBoosterV2

## Installation
1. Download ScreenBoosterV2.exe
2. Place it in any folder
3. Run the EXE (no installation required)

## Usage
- Run ScreenBoosterV2.exe
- Use the menu to configure settings
- Press Ctrl+C to exit

## Features
- Advanced bright object detection (fireball scenarios)
- Dynamic screen brightness/contrast/gamma adjustment
- Safety lock to prevent accidental adjustments
- Performance optimizations
- Custom settings persistence

## Files Created
- screenbooster_settings.json (your custom scene settings)
- screenbooster_config.json (performance configuration)

These files are created automatically and store your preferences.
"""
            
            with open(os.path.join("dist", "README.txt"), "w") as f:
                f.write(readme_content)
            
            print("📄 README.txt created in dist folder")
            print("🎉 Ready for distribution!")
            
        else:
            print("❌ EXE file not found")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    
    return True

if __name__ == "__main__":
    build_exe()
