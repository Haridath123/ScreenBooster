#!/usr/bin/env python3
"""
Simple build script for simple_luma_booster.py
Builds ScreenBoosterV8.exe
"""

import subprocess
import sys
import os
from pathlib import Path

def build():
    """Build simple_luma_booster.py into ScreenBoosterV8.exe"""
    print("Building ScreenBoosterV8.exe from simple_luma_booster.py...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if Path(dir_name).exists():
            import shutil
            shutil.rmtree(dir_name)
    
    # Build with PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=ScreenBoosterV8",
        "--console",
        "simple_luma_booster.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Build successful!")
        print("📦 EXE location: dist/ScreenBoosterV8.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        return False

if __name__ == "__main__":
    build()
