#!/usr/bin/env python3
"""
ScreenBooster V5 - One-Click EXE Builder
========================================

This script builds ScreenBooster V5 into a standalone executable with a single command.
Run: python build_exe.py

Features:
- Automatic dependency detection
- Clean build environment
- Configuration file inclusion
- Multiple build modes
- Error handling and validation
- Post-build testing
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime

class ScreenBoosterBuilder:
    def __init__(self):
        self.project_dir = Path.cwd()
        self.build_dir = self.project_dir / "build"
        self.dist_dir = self.project_dir / "dist"
        self.release_dir = self.project_dir / "release"
        
        # Build configuration
        self.app_name = "ScreenBoosterV5"
        self.main_script = "main.py"
        self.config_files = [
            "screenbooster_profiles.json",
            "screenbooster_config.json"
        ]
        self.doc_files = [
            "README.md",
            "EXTREME_CUSTOMIZATION.md",
            "BUILD_GUIDE.md"
        ]
        
        print(f"🚀 ScreenBooster V5 One-Click Builder")
        print(f"📁 Project Directory: {self.project_dir}")
        print("=" * 50)
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        
        # Check main script exists
        if not (self.project_dir / self.main_script).exists():
            print(f"❌ {self.main_script} not found")
            return False
        
        # Check configuration files exist
        for config_file in self.config_files:
            if not (self.project_dir / config_file).exists():
                print(f"❌ {config_file} not found")
                return False
        
        # Check PyInstaller
        try:
            subprocess.run(["pyinstaller", "--version"], 
                         capture_output=True, check=True)
            print("✅ PyInstaller found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ PyInstaller not found. Installing...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                             check=True)
                print("✅ PyInstaller installed")
            except subprocess.CalledProcessError:
                print("❌ Failed to install PyInstaller")
                return False
        
        print("✅ All prerequisites met")
        return True
    
    def clean_build_environment(self):
        """Clean previous build artifacts"""
        print("🧹 Cleaning build environment...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir, self.release_dir]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  🗑️  Cleaned {dir_path.name}")
        
        # Clean Python cache
        for cache_dir in self.project_dir.rglob("__pycache__"):
            shutil.rmtree(cache_dir)
        
        print("✅ Build environment cleaned")
    
    def create_spec_file(self, mode="release"):
        """Create optimized PyInstaller spec file"""
        print("📝 Creating spec file...")
        
        # Pre-calculate boolean values
        debug_mode = mode == "debug"
        console_mode = True  # Always show console for visibility
        windowed_mode = False  # Never windowed
        
        # Create manifest file for admin privileges
        manifest_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="*"
    name="ScreenBoosterV5"
    type="win32"
  />
  <description>ScreenBooster V5 - Display Adjustment Tool</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>'''
        
        manifest_file = self.project_dir / "app.manifest"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# ScreenBooster V5 PyInstaller Spec File
# Generated automatically by build_exe.py

block_cipher = None

a = Analysis(
    ['{self.main_script}'],
    pathex=[r'{self.project_dir}'],
    binaries=[],
    datas=[
        ('screenbooster_profiles.json', '.'),
        ('screenbooster_config.json', '.')
    ],
    hiddenimports=[
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageGrab',
        'keyboard',
        'ctypes',
        'json',
        'os',
        'sys',
        'time',
        'threading',
        'collections'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'test',
        'pdb',
        'doctest',
        'pydoc',
        'xml',
        'email',
        'sqlite3',
        'matplotlib',
        'scipy'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.app_name}',
    debug={debug_mode},
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_mode},
    windowed={windowed_mode},
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    manifest=r'{manifest_file}',
    icon=None
)
'''
        
        spec_file = self.project_dir / f"{self.app_name}.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✅ Spec file created: {spec_file}")
        return spec_file
    
    def build_executable(self, mode="release"):
        """Build the executable using PyInstaller"""
        print(f"🔨 Building executable ({mode} mode)...")
        
        spec_file = self.create_spec_file(mode)
        
        try:
            cmd = ["pyinstaller", "--clean", str(spec_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ Build completed successfully")
            
            # Check if EXE was created
            exe_path = self.dist_dir / f"{self.app_name}.exe"
            if exe_path.exists():
                file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print(f"  📦 EXE created: {exe_path}")
                print(f"  📏 File size: {file_size:.1f} MB")
                return exe_path
            else:
                print("❌ EXE not found after build")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            print(f"Error output: {e.stderr}")
            return None
    
    def verify_build(self, exe_path):
        """Verify the build was successful"""
        print("🔍 Verifying build...")
        
        if not exe_path or not exe_path.exists():
            print("❌ EXE file not found")
            return False
        
        print("✅ EXE file verified")
        return True
    
    def create_release_package(self, exe_path):
        """Create a complete release package"""
        print("📦 Creating release package...")
        
        self.release_dir.mkdir(exist_ok=True)
        
        # Copy EXE
        release_exe = self.release_dir / f"{self.app_name}.exe"
        shutil.copy2(exe_path, release_exe)
        print(f"  📄 Copied EXE")
        
        # Copy configuration files from project directory
        for config_file in self.config_files:
            src_config = self.project_dir / config_file
            dst_config = self.release_dir / config_file
            if src_config.exists():
                shutil.copy2(src_config, dst_config)
                print(f"  📄 Copied {config_file}")
            else:
                print(f"  ⚠️  Missing {config_file} in project directory")
        
        # Copy documentation
        for doc_file in self.doc_files:
            if (self.project_dir / doc_file).exists():
                shutil.copy2(self.project_dir / doc_file, self.release_dir / doc_file)
        
        # Create version info
        version_info = {
            "version": "4.0",
            "build_date": datetime.now().isoformat(),
            "build_type": "release",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "files": [f.name for f in self.release_dir.iterdir()]
        }
        
        with open(self.release_dir / "version.json", 'w') as f:
            json.dump(version_info, f, indent=2)
        
        # Create quick start guide
        quick_start = f"""# ScreenBooster V5 - Quick Start

## ⚠️ IMPORTANT: RUN AS ADMINISTRATOR

**ScreenBooster MUST be run as Administrator to work!**

### Why?
This application modifies display settings using Windows API calls that require elevated privileges. Without admin rights, the screen adjustments will not work on most Windows systems.

### How to run as Administrator:
1. Right-click on ScreenBoosterV5.exe
2. Select "Run as administrator"
3. Click "Yes" when Windows asks for permission

### Alternative: Rebuild with admin manifest
The build script now creates an EXE that automatically requests admin privileges. Rebuild using:
```bash
python build_exe.py
```

## Installation
1. Extract all files to a folder
2. Run ScreenBoosterV5.exe **as Administrator**
3. No installation required!

## First Run
1. Choose your profile (Game/Movie)
2. Start ScreenBooster (Option 1)
3. Hold Ctrl+Alt to enable adjustments
4. Use hotkeys to fine-tune settings

## Files Included
- ScreenBoosterV5.exe - Main application (run as admin!)
- screenbooster_profiles.json - Profile settings
- screenbooster_config.json - Configuration
- README.md - Complete documentation
- EXTREME_CUSTOMIZATION.md - Advanced tuning
- BUILD_GUIDE.md - Build instructions

## Troubleshooting
- **Screen not changing?** Make sure you're running as Administrator
- **Windows opens but nothing happens?** Right-click → Run as administrator
- **Still not working?** Some display drivers block gamma adjustments

## Support
See README.md for detailed instructions and troubleshooting.

Built: {version_info['build_date']}
Version: {version_info['version']}
"""
        
        with open(self.release_dir / "QUICK_START.md", 'w') as f:
            f.write(quick_start)
        
        print("✅ Release package created")
        return self.release_dir
    
    def build_menu(self):
        """Show build options menu"""
        print("\n🎯 Build Options:")
        print("1. Release Build (Recommended)")
        print("2. Debug Build (With console)")
        print("3. Both Release and Debug")
        print("4. Exit")
        
        while True:
            try:
                choice = input("\nSelect build option (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    return choice
                else:
                    print("❌ Invalid choice. Please select 1-4.")
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Build cancelled")
                return '4'
    
    def run_build(self, mode="release"):
        """Run the complete build process"""
        print(f"\n🚀 Starting {mode} build...")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Clean environment
        self.clean_build_environment()
        
        # Build executable
        exe_path = self.build_executable(mode)
        if not exe_path:
            return False
        
        # Verify build
        if not self.verify_build(exe_path):
            return False
        
        # Create release package
        if mode == "release":
            release_dir = self.create_release_package(exe_path)
            print(f"\n🎉 Build completed successfully!")
            print(f"📦 Release package: {release_dir}")
            print(f"🚀 Ready to distribute!")
        else:
            print(f"\n🎉 Debug build completed!")
            print(f"📦 EXE location: {exe_path}")
            print(f"🔍 Run with console visible for debugging")
        
        return True
    
    def run(self):
        """Main builder interface"""
        try:
            choice = self.build_menu()
            
            if choice == '1':
                self.run_build("release")
            elif choice == '2':
                self.run_build("debug")
            elif choice == '3':
                print("\n🔄 Building both versions...")
                if self.run_build("release"):
                    print("\n" + "="*50)
                    self.run_build("debug")
            elif choice == '4':
                print("👋 Goodbye!")
                return
            
        except KeyboardInterrupt:
            print("\n\n🛑 Build interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main entry point"""
    builder = ScreenBoosterBuilder()
    builder.run()

if __name__ == "__main__":
    main()
