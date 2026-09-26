import cx_Freeze
import sys
import os

# Base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Build options
build_exe_options = {
    "packages": ["numpy", "PIL", "keyboard", "ctypes", "json", "threading", "collections"],
    "excludes": ["tkinter", "matplotlib", "scipy"],
    "include_files": [],
    "zip_include_packages": ["numpy", "PIL"],
    "zip_exclude_packages": []
}

# Setup configuration
setup = {
    "name": "ScreenBooster",
    "version": "2.0.0",
    "description": "Dynamic screen brightness, contrast, and gamma adjustment",
    "author": "ScreenBooster Team",
    "options": {"build_exe": build_exe_options},
    "executables": [
        cx_Freeze.Executable(
            "main.py",
            base_name="ScreenBooster",
            target_name="ScreenBooster.exe",
            icon=None,  # You can add an icon file path here if you have one
            shortcut_name="ScreenBooster",
            shortcut_dir="DesktopFolder"
        )
    ]
}

# Apply setup
cx_Freeze.setup(**setup)
