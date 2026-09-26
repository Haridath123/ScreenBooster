#!/usr/bin/env python3
"""
Simple build script for simple_luma_booster.py
Builds ScreenBooster.exe
"""

import subprocess
import sys
import os
from pathlib import Path

def build():
    """Build simple_luma_booster.py into ScreenBooster.exe"""
    print("Building ScreenBooster.exe from simple_luma_booster.py...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if Path(dir_name).exists():
            import shutil
            shutil.rmtree(dir_name)
    
    # Build with PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=ScreenBooster",
        "--console",
        "simple_luma_booster.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Build successful!")
        print("📦 EXE location: dist/ScreenBooster.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        return False

if __name__ == "__main__":
    build()
