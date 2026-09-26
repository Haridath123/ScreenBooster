import ctypes
import numpy as np
from PIL import ImageGrab
import time
import sys
import json
import os
from collections import deque
import threading
import keyboard

# Hardware access
gdi32 = ctypes.WinDLL('gdi32')
user32 = ctypes.windll.user32

# Configuration (with runtime adjustable defaults)
SMOOTHING = 0.1          # Transition speed (0.05-0.9) - reduced for smoother transitions
REFRESH_RATE = 0.03       # Screen analysis interval (seconds) - reduced from 0.01 to 0.03 (33Hz vs 100Hz)
CONTENT_HISTORY_SIZE = 3 # Frames to analyze

# Scene thresholds (23 total scenes with equal distribution)
VERY_DARK_THRESHOLD = 0.00      # Below this = very dark scene
DARK_THRESHOLD = 0.04             # Dark scene
LOWER_DARK_THRESHOLD = 0.08       # Lower dark scene
MID_DARK_THRESHOLD = 0.12        # Mid dark scene
UPPER_DARK_THRESHOLD = 0.16       # Upper dark scene
LOWER_MID_DARK_THRESHOLD = 0.20   # Lower-mid dark
MID_MID_DARK_THRESHOLD = 0.24     # Mid-mid dark
UPPER_MID_DARK_THRESHOLD = 0.28    # Upper-mid dark
LOWER_MID_THRESHOLD = 0.32       # Lower-mid scene
MID_LOWER_MID_THRESHOLD = 0.36     # Mid-lower-mid
UPPER_LOWER_MID_THRESHOLD = 0.40    # Upper-lower-mid
MID_THRESHOLD = 0.44              # True mid scene (center)
LOWER_UPPER_MID_THRESHOLD = 0.48    # Lower-upper-mid
MID_UPPER_MID_THRESHOLD = 0.52     # Mid-upper-mid
UPPER_MID_THRESHOLD = 0.56       # Upper-mid scene
LOWER_BRIGHT_MID_THRESHOLD = 0.60  # Lower-bright-mid
MID_BRIGHT_MID_THRESHOLD = 0.64     # Mid-bright-mid
UPPER_BRIGHT_MID_THRESHOLD = 0.68   # Upper-bright-mid
LOWER_BRIGHT_THRESHOLD = 0.72      # Lower bright
MID_BRIGHT_THRESHOLD = 0.76        # Mid bright
UPPER_BRIGHT_THRESHOLD = 0.80       # Upper bright
BRIGHT_THRESHOLD = 0.84            # Above this = bright scene

# Performance optimizations
SKIP_FRAMES = 2           # Skip every N frames for analysis (0 = no skip)
FAST_MODE = True          # Enable fast mode optimizations
REGION_SAMPLE_SIZE = 0.05 # Sample smaller regions (5% of original size)

# Configuration adjustment step sizes
SMOOTHING_STEP = 0.01
REFRESH_RATE_STEP = 0.001
THRESHOLD_STEP = 0.01

# Current state
current_gamma = 1.0
current_contrast = 1.0
current_brightness = 1.0
content_history = deque(maxlen=CONTENT_HISTORY_SIZE)
running = True
frame_skip_counter = 0  # For frame skipping
last_analysis_time = 0    # For rate limiting

# Safety lock for keyboard controls
safety_lock_enabled = True  # Default to locked
safety_key_combination = "ctrl+alt"  # Hold this to unlock
last_safety_check = 0
SAFETY_COOLDOWN = 0.1  # seconds between safety checks

# Custom settings for each luma stage (23 total scenes)
custom_settings = {
    "VERY_DARK": {"gamma": 5.0, "contrast": 2.7, "brightness": 1.1},
    "DARK": {"gamma": 4.8, "contrast": 2.5, "brightness": 1.08},
    "LOWER_DARK": {"gamma": 4.5, "contrast": 2.3, "brightness": 1.05},
    "MID_DARK": {"gamma": 4.2, "contrast": 2.1, "brightness": 1.02},
    "UPPER_DARK": {"gamma": 3.8, "contrast": 1.9, "brightness": 1.0},
    "LOWER_MID_DARK": {"gamma": 3.2, "contrast": 1.6, "brightness": 1.0},
    "MID_MID_DARK": {"gamma": 2.6, "contrast": 1.3, "brightness": 1.0},
    "UPPER_MID_DARK": {"gamma": 2.0, "contrast": 1.1, "brightness": 1.0},
    "LOWER_MID": {"gamma": 1.6, "contrast": 1.05, "brightness": 1.0},
    "MID_LOWER_MID": {"gamma": 1.3, "contrast": 1.02, "brightness": 1.0},
    "UPPER_LOWER_MID": {"gamma": 1.1, "contrast": 1.01, "brightness": 1.0},
    "MID": {"gamma": 1.1, "contrast": 1.0, "brightness": 1.0},
    "LOWER_UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0}
}

# Current scene type for tracking
current_scene_type = "MID"

# Adjustment step sizes
GAMMA_STEP = 0.1
CONTRAST_STEP = 0.05
BRIGHTNESS_STEP = 0.05

# Settings file path
SETTINGS_FILE = "screenbooster_settings.json"
CONFIG_FILE = "screenbooster_config.json"

def check_safety_lock():
    """Check if safety lock is disabled (Ctrl+Alt held)"""
    global last_safety_check, safety_lock_enabled
    
    current_time = time.time()
    if current_time - last_safety_check < SAFETY_COOLDOWN:
        return not safety_lock_enabled  # Return cached result
    
    last_safety_check = current_time
    
    # Check if Ctrl+Alt is held down
    ctrl_pressed = keyboard.is_pressed('ctrl')
    alt_pressed = keyboard.is_pressed('alt')
    
    # Safety lock is disabled only when both Ctrl+Alt are held
    safety_lock_enabled = not (ctrl_pressed and alt_pressed)
    
    return not safety_lock_enabled

def show_safety_status():
    """Show current safety lock status"""
    if safety_lock_enabled:
        print("\n🔒 SAFETY LOCK ACTIVE - Hold Ctrl+Alt to enable adjustments")
    else:
        print("\n🔓 SAFETY LOCK DISABLED - Adjustments enabled")

def show_menu():
    print("\n" + "="*60)
    print("           SCREENBOOSTER - MAIN MENU")
    print("="*60)
    print("\n1. Start ScreenBooster (with keyboard controls)")
    print("2. Configuration Menu")
    print("3. Scene Settings Menu")
    print("4. View Current Settings")
    print("5. Check Screen Luma Only")
    print("6. Reset All to Defaults")
    print("7. Exit")
    print("\n" + "="*60)

def show_config_menu():
    """Display configuration menu"""
    print("\n" + "="*60)
    print("           CONFIGURATION MENU")
    print("="*60)
    print(f"\nCurrent Settings:")
    print(f"  Smoothing: {SMOOTHING:.3f} (transition speed)")
    print(f"  Refresh Rate: {REFRESH_RATE:.3f}s ({1000/REFRESH_RATE:.0f}Hz)")
    print(f"  Fast Mode: {'ON' if FAST_MODE else 'OFF'}")
    print(f"  Skip Frames: {SKIP_FRAMES} (0 = no skip)")
    print(f"\nScene Thresholds:")
    print(f"  Very Dark: < {DARK_THRESHOLD:.2f}")
    print(f"  Lower Dark: {DARK_THRESHOLD:.2f} - {LOWER_DARK_THRESHOLD:.2f}")
    print(f"  Mid Dark: {LOWER_DARK_THRESHOLD:.2f} - {MID_DARK_THRESHOLD:.2f}")
    print(f"  Upper Dark: {MID_DARK_THRESHOLD:.2f} - {UPPER_DARK_THRESHOLD:.2f}")
    print(f"  Lower Mid: {UPPER_DARK_THRESHOLD:.2f} - {LOWER_MID_THRESHOLD:.2f}")
    print(f"  Mid: {LOWER_MID_THRESHOLD:.2f} - {MID_THRESHOLD:.2f}")
    print(f"  Upper Mid: {MID_THRESHOLD:.2f} - {UPPER_MID_THRESHOLD:.2f}")
    print(f"  Bright: > {BRIGHT_THRESHOLD:.2f}")
    
    print("\n" + "="*60)
    print("Options:")
    print("1. Adjust Smoothing")
    print("2. Adjust Refresh Rate")
    print("3. Toggle Fast Mode (Current: " + ('ON' if FAST_MODE else 'OFF') + ")")
    print("4. Adjust Skip Frames")
    print("5. Adjust Dark Threshold")
    print("6. Adjust Lower Dark Threshold")
    print("7. Adjust Mid Dark Threshold")
    print("8. Adjust Upper Dark Threshold")
    print("9. Adjust Lower Mid Threshold")
    print("10. Adjust Mid Threshold")
    print("11. Adjust Upper Mid Threshold")
    print("12. Adjust Bright Threshold")
    print("13. Reset Configuration to Defaults")
    print("0. Back to Main Menu")
    print("="*60)

def show_scene_menu():
    """Display scene settings menu"""
    print("\n" + "="*60)
    print("           SCENE SETTINGS MENU")
    print("="*60)
    print("\nSelect Scene Type:")
    print("1. Very Bright")
    print("2. Very Dark")
    print("3. Lower Dark")
    print("4. Mid Dark")
    print("5. Upper Dark")
    print("6. Lower Mid")
    print("7. Mid")
    print("8. Upper Mid")
    print("9. Bright")
    print("0. Back to Main Menu")
    print("="*60)

def show_scene_settings(scene_type):
    """Display settings for a specific scene"""
    settings = custom_settings[scene_type]
    print(f"\n" + "="*60)
    print(f"     {scene_type} SETTINGS")
    print("="*60)
    print(f"\nCurrent Values:")
    print(f"  Gamma: {settings['gamma']:.2f}")
    print(f"  Contrast: {settings['contrast']:.2f}")
    print(f"  Brightness: {settings['brightness']:.2f}")
    
    print("\nOptions:")
    print("1. Adjust Gamma")
    print("2. Adjust Contrast")
    print("3. Adjust Brightness")
    print("4. Reset to Defaults")
    print("0. Back to Scene Menu")
    print("="*60)

def adjust_value_menu(current_value, min_val, max_val, step, name):
    """Interactive menu for adjusting a value"""
    while True:
        print(f"\n{name}: {current_value:.3f}")
        print("Options:")
        print(f"1. Increase (+{step})")
        print(f"2. Decrease (-{step})")
        print("3. Large Increase (+10x)")
        print("4. Large Decrease (-10x)")
        print("5. Enter Custom Value")
        print("0. Done")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            current_value = min(max_val, current_value + step)
        elif choice == "2":
            current_value = max(min_val, current_value - step)
        elif choice == "3":
            current_value = min(max_val, current_value + step * 10)
        elif choice == "4":
            current_value = max(min_val, current_value - step * 10)
        elif choice == "5":
            try:
                new_val = float(input(f"Enter new value ({min_val}-{max_val}): "))
                if min_val <= new_val <= max_val:
                    current_value = new_val
                else:
                    print(f"Value must be between {min_val} and {max_val}")
            except ValueError:
                print("Invalid number")
        elif choice == "0":
            break
        else:
            print("Invalid choice")
    
    return current_value

def config_menu():
    """Handle configuration menu"""
    global SMOOTHING, REFRESH_RATE, FAST_MODE, SKIP_FRAMES
    global DARK_THRESHOLD, LOWER_DARK_THRESHOLD, MID_DARK_THRESHOLD, UPPER_DARK_THRESHOLD
    global LOWER_MID_THRESHOLD, MID_THRESHOLD, UPPER_MID_THRESHOLD, BRIGHT_THRESHOLD
    
    while True:
        show_config_menu()
        choice = input("\nEnter choice (0-13): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            SMOOTHING = adjust_value_menu(SMOOTHING, 0.05, 0.9, SMOOTHING_STEP, "Smoothing")
        elif choice == "2":
            REFRESH_RATE = adjust_value_menu(REFRESH_RATE, 0.001, 0.1, REFRESH_RATE_STEP, "Refresh Rate (seconds)")
        elif choice == "3":
            FAST_MODE = not FAST_MODE
            print(f"Fast Mode: {'ON' if FAST_MODE else 'OFF'}")
            print("Fast Mode captures smaller areas and uses simplified analysis")
            input("Press Enter to continue...")
        elif choice == "4":
            SKIP_FRAMES = int(adjust_value_menu(SKIP_FRAMES, 0, 10, 1, "Skip Frames"))
        elif choice == "5":
            DARK_THRESHOLD = adjust_value_menu(DARK_THRESHOLD, 0.01, LOWER_DARK_THRESHOLD - 0.01, THRESHOLD_STEP, "Dark Threshold")
        elif choice == "6":
            LOWER_DARK_THRESHOLD = adjust_value_menu(LOWER_DARK_THRESHOLD, DARK_THRESHOLD + 0.01, MID_DARK_THRESHOLD - 0.01, THRESHOLD_STEP, "Lower Dark Threshold")
        elif choice == "7":
            MID_DARK_THRESHOLD = adjust_value_menu(MID_DARK_THRESHOLD, LOWER_DARK_THRESHOLD + 0.01, UPPER_DARK_THRESHOLD - 0.01, THRESHOLD_STEP, "Mid Dark Threshold")
        elif choice == "8":
            UPPER_DARK_THRESHOLD = adjust_value_menu(UPPER_DARK_THRESHOLD, MID_DARK_THRESHOLD + 0.01, LOWER_MID_THRESHOLD - 0.01, THRESHOLD_STEP, "Upper Dark Threshold")
        elif choice == "9":
            LOWER_MID_THRESHOLD = adjust_value_menu(LOWER_MID_THRESHOLD, UPPER_DARK_THRESHOLD + 0.01, MID_THRESHOLD - 0.01, THRESHOLD_STEP, "Lower Mid Threshold")
        elif choice == "10":
            MID_THRESHOLD = adjust_value_menu(MID_THRESHOLD, LOWER_MID_THRESHOLD + 0.01, UPPER_MID_THRESHOLD - 0.01, THRESHOLD_STEP, "Mid Threshold")
        elif choice == "11":
            UPPER_MID_THRESHOLD = adjust_value_menu(UPPER_MID_THRESHOLD, MID_THRESHOLD + 0.01, BRIGHT_THRESHOLD - 0.01, THRESHOLD_STEP, "Upper Mid Threshold")
        elif choice == "12":
            BRIGHT_THRESHOLD = adjust_value_menu(BRIGHT_THRESHOLD, UPPER_MID_THRESHOLD + 0.01, 0.99, THRESHOLD_STEP, "Bright Threshold")
        elif choice == "13":
            if input("Reset all configuration to defaults? (y/n): ").lower() == 'y':
                reset_config()
        else:
            print("Invalid choice")
    
    save_config()

def scene_menu():
    """Handle scene settings menu"""
    scene_types = [
        "VERY_BRIGHT", "VERY_DARK", "LOWER_DARK", "MID_DARK", 
        "UPPER_DARK", "LOWER_MID", "MID", "UPPER_MID", "BRIGHT"
    ]
    
    while True:
        show_scene_menu()
        choice = input("\nEnter choice (0-9): ").strip()
        
        if choice == "0":
            break
        elif choice in [str(i) for i in range(1, 10)]:
            scene_type = scene_types[int(choice) - 1]
            scene_settings_menu(scene_type)
        else:
            print("Invalid choice")

def scene_settings_menu(scene_type):
    """Handle settings for a specific scene"""
    while True:
        show_scene_settings(scene_type)
        choice = input("\nEnter choice (0-4): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            custom_settings[scene_type]["gamma"] = adjust_value_menu(
                custom_settings[scene_type]["gamma"], 0.1, 5.0, GAMMA_STEP, "Gamma"
            )
        elif choice == "2":
            custom_settings[scene_type]["contrast"] = adjust_value_menu(
                custom_settings[scene_type]["contrast"], 0.1, 3.0, CONTRAST_STEP, "Contrast"
            )
        elif choice == "3":
            custom_settings[scene_type]["brightness"] = adjust_value_menu(
                custom_settings[scene_type]["brightness"], 0.1, 2.0, BRIGHTNESS_STEP, "Brightness"
            )
        elif choice == "4":
            if input(f"Reset {scene_type} to defaults? (y/n): ").lower() == 'y':
                defaults = {
                    "VERY_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 0.96},
                    "VERY_DARK": {"gamma": 3.1, "contrast": 1.6, "brightness": 1.0},
                    "LOWER_DARK": {"gamma": 2.9, "contrast": 1.9, "brightness": 0.9},
                    "MID_DARK": {"gamma": 2.6, "contrast": 1.8, "brightness": 0.8},
                    "UPPER_DARK": {"gamma": 2.0, "contrast": 1.5, "brightness": 0.7},
                    "LOWER_MID": {"gamma": 1.6, "contrast": 1.3, "brightness": 0.9},
                    "MID": {"gamma": 1.1, "contrast": 1.1, "brightness": 1.0},
                    "UPPER_MID": {"gamma": 1.1, "contrast": 1.0, "brightness": 1.0},
                    "BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0}
                }
                custom_settings[scene_type] = defaults[scene_type].copy()
                print(f"Reset {scene_type} to defaults")
        else:
            print("Invalid choice")
    
    save_custom_settings()

def view_current_settings():
    """Display all current settings"""
    print("\n" + "="*60)
    print("           CURRENT SETTINGS")
    print("="*60)
    
    print("\nConfiguration:")
    print(f"  Smoothing: {SMOOTHING:.3f}")
    print(f"  Refresh Rate: {REFRESH_RATE:.3f}s ({1000/REFRESH_RATE:.0f}Hz)")
    
    print("\nScene Thresholds:")
    print(f"  Very Dark: < {DARK_THRESHOLD:.2f}")
    print(f"  Lower Dark: {DARK_THRESHOLD:.2f} - {LOWER_DARK_THRESHOLD:.2f}")
    print(f"  Mid Dark: {LOWER_DARK_THRESHOLD:.2f} - {MID_DARK_THRESHOLD:.2f}")
    print(f"  Upper Dark: {MID_DARK_THRESHOLD:.2f} - {UPPER_DARK_THRESHOLD:.2f}")
    print(f"  Lower Mid: {UPPER_DARK_THRESHOLD:.2f} - {LOWER_MID_THRESHOLD:.2f}")
    print(f"  Mid: {LOWER_MID_THRESHOLD:.2f} - {MID_THRESHOLD:.2f}")
    print(f"  Upper Mid: {MID_THRESHOLD:.2f} - {UPPER_MID_THRESHOLD:.2f}")
    print(f"  Bright: > {BRIGHT_THRESHOLD:.2f}")
    
    print("\nScene Settings:")
    for scene_type, settings in custom_settings.items():
        print(f"  {scene_type}: γ{settings['gamma']:.2f} C{settings['contrast']:.2f} B{settings['brightness']:.2f}")
    
    print("="*60)
    input("\nPress Enter to continue...")

def reset_all_defaults():
    """Reset everything to defaults"""
    if input("Reset ALL settings to defaults? (y/n): ").lower() == 'y':
        reset_config()
        # Reset scene settings
        defaults = {
            "VERY_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 0.96},
            "VERY_DARK": {"gamma": 3.1, "contrast": 1.6, "brightness": 1.0},
            "LOWER_DARK": {"gamma": 2.9, "contrast": 1.9, "brightness": 0.9},
            "MID_DARK": {"gamma": 2.6, "contrast": 1.8, "brightness": 0.8},
            "UPPER_DARK": {"gamma": 2.0, "contrast": 1.5, "brightness": 0.7},
            "LOWER_MID": {"gamma": 1.6, "contrast": 1.3, "brightness": 0.9},
            "MID": {"gamma": 1.1, "contrast": 1.1, "brightness": 1.0},
            "UPPER_MID": {"gamma": 1.1, "contrast": 1.0, "brightness": 1.0},
            "BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0}
        }
        global custom_settings
        custom_settings = defaults.copy()
        save_custom_settings()
        print("All settings reset to defaults")
    input("Press Enter to continue...")

def load_config():
    """Load configuration from file"""
    global SMOOTHING, REFRESH_RATE, CONTENT_HISTORY_SIZE, FAST_MODE, SKIP_FRAMES
    global DARK_THRESHOLD, LOWER_DARK_THRESHOLD, MID_DARK_THRESHOLD, UPPER_DARK_THRESHOLD
    global LOWER_MID_THRESHOLD, MID_THRESHOLD, UPPER_MID_THRESHOLD, BRIGHT_THRESHOLD
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Load configuration values
                SMOOTHING = config.get('SMOOTHING', SMOOTHING)
                REFRESH_RATE = config.get('REFRESH_RATE', REFRESH_RATE)
                CONTENT_HISTORY_SIZE = config.get('CONTENT_HISTORY_SIZE', CONTENT_HISTORY_SIZE)
                FAST_MODE = config.get('FAST_MODE', FAST_MODE)
                SKIP_FRAMES = config.get('SKIP_FRAMES', SKIP_FRAMES)
                DARK_THRESHOLD = config.get('DARK_THRESHOLD', DARK_THRESHOLD)
                LOWER_DARK_THRESHOLD = config.get('LOWER_DARK_THRESHOLD', LOWER_DARK_THRESHOLD)
                MID_DARK_THRESHOLD = config.get('MID_DARK_THRESHOLD', MID_DARK_THRESHOLD)
                UPPER_DARK_THRESHOLD = config.get('UPPER_DARK_THRESHOLD', UPPER_DARK_THRESHOLD)
                LOWER_MID_THRESHOLD = config.get('LOWER_MID_THRESHOLD', LOWER_MID_THRESHOLD)
                MID_THRESHOLD = config.get('MID_THRESHOLD', MID_THRESHOLD)
                UPPER_MID_THRESHOLD = config.get('UPPER_MID_THRESHOLD', UPPER_MID_THRESHOLD)
                BRIGHT_THRESHOLD = config.get('BRIGHT_THRESHOLD', BRIGHT_THRESHOLD)
                print(f"Configuration loaded from {CONFIG_FILE}")
    except Exception as e:
        print(f"Could not load configuration: {e}")

def save_config():
    """Save configuration to file"""
    config = {
        'SMOOTHING': SMOOTHING,
        'REFRESH_RATE': REFRESH_RATE,
        'CONTENT_HISTORY_SIZE': CONTENT_HISTORY_SIZE,
        'FAST_MODE': FAST_MODE,
        'SKIP_FRAMES': SKIP_FRAMES,
        'DARK_THRESHOLD': DARK_THRESHOLD,
        'LOWER_DARK_THRESHOLD': LOWER_DARK_THRESHOLD,
        'MID_DARK_THRESHOLD': MID_DARK_THRESHOLD,
        'UPPER_DARK_THRESHOLD': UPPER_DARK_THRESHOLD,
        'LOWER_MID_THRESHOLD': LOWER_MID_THRESHOLD,
        'MID_THRESHOLD': MID_THRESHOLD,
        'UPPER_MID_THRESHOLD': UPPER_MID_THRESHOLD,
        'BRIGHT_THRESHOLD': BRIGHT_THRESHOLD
    }
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Could not save configuration: {e}")

def adjust_config_setting(setting_type, increase=True):
    """Adjust configuration settings"""
    global SMOOTHING, REFRESH_RATE, CONTENT_HISTORY_SIZE
    global DARK_THRESHOLD, LOWER_DARK_THRESHOLD, MID_DARK_THRESHOLD, UPPER_DARK_THRESHOLD
    global LOWER_MID_THRESHOLD, MID_THRESHOLD, UPPER_MID_THRESHOLD, BRIGHT_THRESHOLD
    
    step = 0
    if setting_type == 'smoothing':
        step = SMOOTHING_STEP
        if increase:
            new_value = min(0.9, SMOOTHING + step)
        else:
            new_value = max(0.05, SMOOTHING - step)
        SMOOTHING = new_value
        print(f"Smoothing: {SMOOTHING:.3f}")
        
    elif setting_type == 'refresh_rate':
        step = REFRESH_RATE_STEP
        if increase:
            new_value = min(0.1, REFRESH_RATE + step)
        else:
            new_value = max(0.001, REFRESH_RATE - step)
        REFRESH_RATE = new_value
        print(f"Refresh Rate: {REFRESH_RATE:.3f}s ({1000/REFRESH_RATE:.0f}Hz)")
        
    elif setting_type == 'dark_threshold':
        step = THRESHOLD_STEP
        if increase:
            new_value = min(LOWER_DARK_THRESHOLD - 0.01, DARK_THRESHOLD + step)
        else:
            new_value = max(0.01, DARK_THRESHOLD - step)
        DARK_THRESHOLD = new_value
        print(f"Dark Threshold: {DARK_THRESHOLD:.2f}")
        
    elif setting_type == 'lower_dark_threshold':
        step = THRESHOLD_STEP
        if increase:
            new_value = min(MID_DARK_THRESHOLD - 0.01, LOWER_DARK_THRESHOLD + step)
        else:
            new_value = max(DARK_THRESHOLD + 0.01, LOWER_DARK_THRESHOLD - step)
        LOWER_DARK_THRESHOLD = new_value
        print(f"Lower Dark Threshold: {LOWER_DARK_THRESHOLD:.2f}")
        
    elif setting_type == 'mid_dark_threshold':
        step = THRESHOLD_STEP
        if increase:
            new_value = min(UPPER_DARK_THRESHOLD - 0.01, MID_DARK_THRESHOLD + step)
        else:
            new_value = max(LOWER_DARK_THRESHOLD + 0.01, MID_DARK_THRESHOLD - step)
        MID_DARK_THRESHOLD = new_value
        print(f"Mid Dark Threshold: {MID_DARK_THRESHOLD:.2f}")
        
    elif setting_type == 'upper_dark_threshold':
        step = THRESHOLD_STEP
        if increase:
            new_value = min(LOWER_MID_THRESHOLD - 0.01, UPPER_DARK_THRESHOLD + step)
        else:
            new_value = max(MID_DARK_THRESHOLD + 0.01, UPPER_DARK_THRESHOLD - step)
        UPPER_DARK_THRESHOLD = new_value
        print(f"Upper Dark Threshold: {UPPER_DARK_THRESHOLD:.2f}")
        
    elif setting_type == 'lower_mid_threshold':
        step = THRESHOLD_STEP
        if increase:
            new_value = min(MID_THRESHOLD - 0.01, LOWER_MID_THRESHOLD + step)
        else:
            new_value = max(UPPER_DARK_THRESHOLD + 0.01, LOWER_MID_THRESHOLD - step)
        LOWER_MID_THRESHOLD = new_value
        print(f"Lower Mid Threshold: {LOWER_MID_THRESHOLD:.2f}")
        
    elif setting_type == 'mid_threshold':
        step = THRESHOLD_STEP
        if increase:
            new_value = min(UPPER_MID_THRESHOLD - 0.01, MID_THRESHOLD + step)
        else:
            new_value = max(LOWER_MID_THRESHOLD + 0.01, MID_THRESHOLD - step)
        MID_THRESHOLD = new_value
        print(f"Mid Threshold: {MID_THRESHOLD:.2f}")
        
    elif setting_type == 'upper_mid_threshold':
        step = THRESHOLD_STEP
        if increase:
            new_value = min(BRIGHT_THRESHOLD - 0.01, UPPER_MID_THRESHOLD + step)
        else:
            new_value = max(MID_THRESHOLD + 0.01, UPPER_MID_THRESHOLD - step)
        UPPER_MID_THRESHOLD = new_value
        print(f"Upper Mid Threshold: {UPPER_MID_THRESHOLD:.2f}")
        
    elif setting_type == 'bright_threshold':
        step = THRESHOLD_STEP
        if increase:
            new_value = min(0.99, BRIGHT_THRESHOLD + step)
        else:
            new_value = max(UPPER_MID_THRESHOLD + 0.01, MID_BRIGHT_THRESHOLD - step)
        MID_BRIGHT_THRESHOLD = new_value
        print(f"Mid Bright Threshold: {MID_BRIGHT_THRESHOLD:.2f}")
    
    # Save configuration
    save_config()

def load_custom_settings():
    global custom_settings
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                loaded = json.load(f)
                # Merge with defaults
                for scene_type, settings in loaded.items():
                    if scene_type in custom_settings:
                        custom_settings[scene_type].update(settings)
                print(f"Custom settings loaded from {SETTINGS_FILE}")
    except Exception as e:
        print(f"Could not load settings: {e}")

def save_custom_settings():
    """Save custom settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(custom_settings, f, indent=2)
        print(f"Custom settings saved to {SETTINGS_FILE}")
    except Exception as e:
        print(f"Could not save settings: {e}")

def get_scene_type(luma, highlight_ratio, bright_in_dark=False, overall_bright=False, high_contrast=False, dark_with_highlights=False):
    """Advanced scene detection - 23 scene system with equal distribution"""
    
    # Priority 1: Special scenarios (this is the ONLY system now)
    if bright_in_dark:
        # Fireball scenario - force bright scene to reduce brightness
        if highlight_ratio > 0.15:
            return "BRIGHT"
        elif highlight_ratio > 0.08:
            return "UPPER_BRIGHT"
        else:
            return "MID_BRIGHT"
    
    if overall_bright:
        # Everything is bright - normal bright handling
        if luma > 0.80:
            return "BRIGHT"
        elif luma > UPPER_BRIGHT_THRESHOLD:
            return "UPPER_BRIGHT"
        else:
            return "MID_BRIGHT"
    
    if high_contrast:
        # Mixed lighting - use enhanced luma but with contrast weighting
        if luma > UPPER_MID_THRESHOLD:
            return "UPPER_MID"
        elif luma > MID_THRESHOLD:
            return "MID"
        elif luma > LOWER_MID_THRESHOLD:
            return "LOWER_MID"
        else:
            return "UPPER_MID_DARK"
    
    if dark_with_highlights:
        # Dark with highlights - lean towards slightly brighter scenes
        if highlight_ratio > 0.05:
            return "LOWER_MID"
        else:
            return "UPPER_DARK"
    
    # Priority 2: Fallback detection (23 scene system)
    if highlight_ratio > 0.8:
        return "BRIGHT"
    elif luma < VERY_DARK_THRESHOLD:
        return "VERY_DARK"
    elif luma < DARK_THRESHOLD:
        return "DARK"
    elif luma < LOWER_DARK_THRESHOLD:
        return "LOWER_DARK"
    elif luma < MID_DARK_THRESHOLD:
        return "MID_DARK"
    elif luma < UPPER_DARK_THRESHOLD:
        return "UPPER_DARK"
    elif luma < LOWER_MID_DARK_THRESHOLD:
        return "LOWER_MID_DARK"
    elif luma < MID_MID_DARK_THRESHOLD:
        return "MID_MID_DARK"
    elif luma < UPPER_MID_DARK_THRESHOLD:
        return "UPPER_MID_DARK"
    elif luma < LOWER_MID_THRESHOLD:
        return "LOWER_MID"
    elif luma < MID_LOWER_MID_THRESHOLD:
        return "MID_LOWER_MID"
    elif luma < UPPER_LOWER_MID_THRESHOLD:
        return "UPPER_LOWER_MID"
    elif luma < MID_THRESHOLD:
        return "MID"
    elif luma < LOWER_UPPER_MID_THRESHOLD:
        return "LOWER_UPPER_MID"
    elif luma < MID_UPPER_MID_THRESHOLD:
        return "MID_UPPER_MID"
    elif luma < UPPER_MID_THRESHOLD:
        return "UPPER_MID"
    elif luma < LOWER_BRIGHT_MID_THRESHOLD:
        return "LOWER_BRIGHT_MID"
    elif luma < MID_BRIGHT_MID_THRESHOLD:
        return "MID_BRIGHT_MID"
    elif luma < UPPER_BRIGHT_MID_THRESHOLD:
        return "UPPER_BRIGHT_MID"
    elif luma < LOWER_BRIGHT_THRESHOLD:
        return "LOWER_BRIGHT"
    elif luma < MID_BRIGHT_THRESHOLD:
        return "MID_BRIGHT"
    elif luma < UPPER_BRIGHT_THRESHOLD:
        return "UPPER_BRIGHT"
    else:
        return "BRIGHT"

def adjust_current_setting(setting_type, increase=True):
    """Adjust current setting and save it for the current scene type"""
    global current_scene_type, custom_settings
    
    step = GAMMA_STEP if setting_type == "gamma" else CONTRAST_STEP if setting_type == "contrast" else BRIGHTNESS_STEP
    if not increase:
        step = -step
    
    # Adjust current value
    if setting_type == "gamma":
        new_value = max(0.1, min(5.0, custom_settings[current_scene_type]["gamma"] + step))
        custom_settings[current_scene_type]["gamma"] = new_value
        print(f"Gamma for {current_scene_type}: {new_value:.2f}")
    elif setting_type == "contrast":
        new_value = max(0.1, min(3.0, custom_settings[current_scene_type]["contrast"] + step))
        custom_settings[current_scene_type]["contrast"] = new_value
        print(f"Contrast for {current_scene_type}: {new_value:.2f}")
    elif setting_type == "brightness":
        new_value = max(0.1, min(2.0, custom_settings[current_scene_type]["brightness"] + step))
        custom_settings[current_scene_type]["brightness"] = new_value
        print(f"Brightness for {current_scene_type}: {new_value:.2f}")
    
    # Save settings
    save_custom_settings()

def reset_config():
    """Reset configuration to defaults"""
    global SMOOTHING, REFRESH_RATE, CONTENT_HISTORY_SIZE
    global DARK_THRESHOLD, LOWER_DARK_THRESHOLD, MID_DARK_THRESHOLD, UPPER_DARK_THRESHOLD
    global LOWER_MID_THRESHOLD, MID_THRESHOLD, UPPER_MID_THRESHOLD, BRIGHT_THRESHOLD
    
    # Reset to defaults
    SMOOTHING = 0.1
    REFRESH_RATE = 0.01
    CONTENT_HISTORY_SIZE = 3
    DARK_THRESHOLD = 0.05
    LOWER_DARK_THRESHOLD = 0.10
    MID_DARK_THRESHOLD = 0.20
    UPPER_DARK_THRESHOLD = 0.30
    LOWER_MID_THRESHOLD = 0.45
    MID_THRESHOLD = 0.50
    UPPER_MID_THRESHOLD = 0.65
    BRIGHT_THRESHOLD = 0.85
    
    print("Configuration reset to defaults")
    save_config()

def keyboard_listener():
    """Listen for keyboard inputs with safety lock"""
    print("\nKeyboard controls enabled:")
    print("\n=== SAFETY LOCK ===")
    print("🔒 Safety Lock: ACTIVE by default")
    print("   Hold Ctrl+Alt to enable adjustments")
    print("   This prevents accidental changes while typing")
    
    print("\n=== Gamma/Contrast/Brightness Controls ===")
    print("  (Hold Ctrl+Alt +) G (increase) / Shift+G (decrease)")
    print("  (Hold Ctrl+Alt +) C (increase) / Shift+C (decrease)")
    print("  (Hold Ctrl+Alt +) B (increase) / Shift+B (decrease)")
    print("  (Hold Ctrl+Alt +) R (reset ALL scenes to defaults)")
    print("  (Hold Ctrl+Alt +) S (manually save settings)")
    
    print("\n=== Configuration Controls ===")
    print("  (Hold Ctrl+Alt +) 1 (increase) / Shift+1 (decrease)")
    print("  (Hold Ctrl+Alt +) 2 (increase) / Shift+2 (decrease)")
    print("  (Hold Ctrl+Alt +) 3-0 for thresholds")
    print("  (Hold Ctrl+Alt +) Shift+R (reset all config to defaults)")
    
    safety_status_shown = False
    
    while running:
        try:
            # Check if safety lock is disabled
            can_adjust = check_safety_lock()
            
            # Show status when it changes
            if can_adjust and not safety_status_shown:
                print("\n🔓 Safety Lock Disabled - Adjustments enabled")
                safety_status_shown = True
            elif not can_adjust and safety_status_shown:
                print("\n🔒 Safety Lock Active - Hold Ctrl+Alt to enable adjustments")
                safety_status_shown = False
            
            # Only process adjustments if safety lock is disabled
            if can_adjust:
                # Original controls
                if keyboard.is_pressed('g') and not keyboard.is_pressed('shift'):
                    adjust_current_setting('gamma', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('g') and keyboard.is_pressed('shift'):
                    adjust_current_setting('gamma', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('c') and not keyboard.is_pressed('shift'):
                    adjust_current_setting('contrast', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('c') and keyboard.is_pressed('shift'):
                    adjust_current_setting('contrast', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('b') and not keyboard.is_pressed('shift'):
                    adjust_current_setting('brightness', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('b') and keyboard.is_pressed('shift'):
                    adjust_current_setting('brightness', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('r'):
                    # Reset ALL scenes to defaults (using exact current defaults)
                    global custom_settings
                    custom_settings = {
                        "VERY_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 0.96},
                        "VERY_DARK": {"gamma": 3.1, "contrast": 1.6, "brightness": 1.0},
                        "LOWER_DARK": {"gamma": 2.9, "contrast": 1.9, "brightness": 0.9},
                        "MID_DARK": {"gamma": 2.6, "contrast": 1.8, "brightness": 0.8},
                        "UPPER_DARK": {"gamma": 2.0, "contrast": 1.5, "brightness": 0.7},
                        "LOWER_MID": {"gamma": 1.6, "contrast": 1.3, "brightness": 0.9},
                        "MID": {"gamma": 1.1, "contrast": 1.1, "brightness": 1.0},
                        "UPPER_MID": {"gamma": 1.1, "contrast": 1.0, "brightness": 1.0},
                        "BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0}
                    }
                    print(f"🔄 ALL scenes reset to defaults!")
                    save_custom_settings()
                    time.sleep(0.5)
                elif keyboard.is_pressed('s') and not keyboard.is_pressed('ctrl'):
                    save_custom_settings()
                    time.sleep(0.5)
                
                # Configuration controls
                elif keyboard.is_pressed('1') and not keyboard.is_pressed('shift'):
                    adjust_config_setting('smoothing', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('1') and keyboard.is_pressed('shift'):
                    adjust_config_setting('smoothing', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('2') and not keyboard.is_pressed('shift'):
                    adjust_config_setting('refresh_rate', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('2') and keyboard.is_pressed('shift'):
                    adjust_config_setting('refresh_rate', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('3') and not keyboard.is_pressed('shift'):
                    adjust_config_setting('dark_threshold', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('3') and keyboard.is_pressed('shift'):
                    adjust_config_setting('dark_threshold', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('4') and not keyboard.is_pressed('shift'):
                    adjust_config_setting('lower_dark_threshold', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('4') and keyboard.is_pressed('shift'):
                    adjust_config_setting('lower_dark_threshold', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('5') and not keyboard.is_pressed('shift'):
                    adjust_config_setting('mid_dark_threshold', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('5') and keyboard.is_pressed('shift'):
                    adjust_config_setting('mid_dark_threshold', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('6') and not keyboard.is_pressed('shift'):
                    adjust_config_setting('upper_dark_threshold', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('6') and keyboard.is_pressed('shift'):
                    adjust_config_setting('upper_dark_threshold', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('7') and not keyboard.is_pressed('shift'):
                    adjust_config_setting('lower_mid_threshold', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('7') and keyboard.is_pressed('shift'):
                    adjust_config_setting('lower_mid_threshold', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('8') and not keyboard.is_pressed('shift'):
                    adjust_config_setting('mid_threshold', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('8') and keyboard.is_pressed('shift'):
                    adjust_config_setting('mid_threshold', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('9') and not keyboard.is_pressed('shift'):
                    adjust_config_setting('upper_mid_threshold', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('9') and keyboard.is_pressed('shift'):
                    adjust_config_setting('upper_mid_threshold', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('0') and not keyboard.is_pressed('shift'):
                    adjust_config_setting('bright_threshold', increase=True)
                    time.sleep(0.2)
                elif keyboard.is_pressed('0') and keyboard.is_pressed('shift'):
                    adjust_config_setting('bright_threshold', increase=False)
                    time.sleep(0.2)
                elif keyboard.is_pressed('r') and keyboard.is_pressed('shift'):
                    reset_config()
                    time.sleep(0.5)
            
            time.sleep(0.01)
        except:
            pass

def apply_settings(gamma, contrast, brightness=1.0):
    """Apply hardware gamma, contrast, and brightness adjustments using optimized 16-bit precision"""
    try:
        ramp = (ctypes.c_ushort * 768)()
        
        # Optimized: Calculate only 256 values but with 16-bit precision math
        for i in range(256):
            n = i / 255.0  # 8-bit input
            
            # Apply brightness first (adds/subtracts constant value)
            n = n * brightness
            
            # Apply gamma with 16-bit precision simulation
            gamma_corrected = n ** (1.0 / gamma)
            
            # Apply contrast using linear method (16-bit precision simulation)
            if contrast != 1.0:
                if contrast > 1.0:
                    # Increase contrast using linear method
                    contrast_adjusted = (gamma_corrected - 0.5) * contrast + 0.5
                    gamma_corrected = max(0.0, min(1.0, contrast_adjusted))
                    
                    # Add highlight boost for very bright areas
                    if gamma_corrected > 0.7:
                        highlight_boost = (gamma_corrected - 0.7) * 0.2
                        gamma_corrected = min(1.0, gamma_corrected + highlight_boost)
                else:
                    # Decrease contrast
                    contrast_adjusted = (gamma_corrected - 0.5) * contrast + 0.5
                    gamma_corrected = max(0.0, min(1.0, contrast_adjusted))
            
            # Convert to 16-bit for hardware (simulates 16-bit precision)
            res = int(gamma_corrected * 65535.0)
            ramp[i] = ramp[i + 256] = ramp[i + 512] = res
        
        hdc = user32.GetDC(None)
        if gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(ramp)):
            user32.ReleaseDC(None, hdc)
            return True
        user32.ReleaseDC(None, hdc)
    except Exception as e:
        print(f"Error: {e}")
    return False

def analyze_screen():
    """Analyze multiple screen areas dynamically based on current resolution with optimizations"""
    global frame_skip_counter, last_analysis_time
    
    try:
        # Frame skipping - skip analysis every N frames
        if SKIP_FRAMES > 0:
            frame_skip_counter += 1
            if frame_skip_counter <= SKIP_FRAMES:
                # Return cached values or simple estimate
                return 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5
            frame_skip_counter = 0
        
        # Rate limiting - don't analyze too frequently
        current_time = time.time()
        if current_time - last_analysis_time < REFRESH_RATE:
            time.sleep(0.001)  # Tiny sleep to yield CPU
        last_analysis_time = current_time
        
        # Dynamically get current screen resolution
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        # Fast mode optimizations
        if FAST_MODE:
            # Capture smaller area for faster processing
            sample_width = int(screen_width * 0.3)  # 30% of width
            sample_height = int(screen_height * 0.3)  # 30% of height
            x_offset = (screen_width - sample_width) // 2
            y_offset = (screen_height - sample_height) // 2
            
            # Single center capture instead of full screen
            full_screen = ImageGrab.grab(bbox=(x_offset, y_offset, x_offset + sample_width, y_offset + sample_height)).convert('RGB')
            full_array = np.array(full_screen)
            
            # Simplified sampling - just center and corners
            sample_ratios = [
                (0.3, 0.3, 0.7, 0.7),    # Center
                (0.05, 0.05, 0.15, 0.15), # Top-left
                (0.85, 0.05, 0.95, 0.15), # Top-right
                (0.05, 0.85, 0.15, 0.95), # Bottom-left
                (0.85, 0.85, 0.95, 0.95), # Bottom-right
            ]
        else:
            # Original full screen capture
            full_screen = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height)).convert('RGB')
            full_array = np.array(full_screen)
            
            # Original comprehensive sampling
            sample_ratios = [
                # Center (larger - most important area)
                (0.4, 0.4, 0.6, 0.6),  # Center (20% of screen)
                
                # Corners
                (0.01, 0.01, 0.08, 0.08),   # Top-left
                (0.92, 0.01, 0.99, 0.08),   # Top-right
                (0.01, 0.92, 0.08, 0.99),   # Bottom-left
                (0.92, 0.92, 0.99, 0.99),   # Bottom-right
                
                # Mid-edges
                (0.46, 0.01, 0.54, 0.08),   # Top-center
                (0.46, 0.92, 0.54, 0.99),   # Bottom-center
                (0.01, 0.46, 0.08, 0.54),   # Left-center
                (0.92, 0.46, 0.99, 0.54),   # Right-center
                
                # Center-left and center-right
                (0.3, 0.45, 0.38, 0.55),    # Center-left
                (0.62, 0.45, 0.7, 0.55),    # Center-right
                
                # In-between diagonal points
                (0.22, 0.22, 0.28, 0.28),   # Top-left quadrant
                (0.72, 0.22, 0.78, 0.28),   # Top-right quadrant
                (0.22, 0.72, 0.28, 0.78),   # Bottom-left quadrant
                (0.72, 0.72, 0.78, 0.78),   # Bottom-right quadrant
            ]
        
        all_luma_data = []
        
        for rx1, ry1, rx2, ry2 in sample_ratios:
            # Convert percentages to actual pixel coordinates
            if FAST_MODE:
                # Use relative coordinates within the smaller captured area
                x1 = int(rx1 * sample_width)
                y1 = int(ry1 * sample_height)
                x2 = int(rx2 * sample_width)
                y2 = int(ry2 * sample_height)
            else:
                # Use full screen coordinates
                x1, y1 = int(rx1 * screen_width), int(ry1 * screen_height)
                x2, y2 = int(rx2 * screen_width), int(ry2 * screen_height)
            
            try:
                # Extract region from full screen array
                region_array = full_array[y1:y2, x1:x2]
                
                # Fast mode: sample every 2nd pixel for faster processing
                if FAST_MODE and region_array.size > 1000:
                    region_array = region_array[::2, ::2]
                
                # Calculate BT.709 luma for this region
                r_channel = region_array[:, :, 0] / 255.0
                g_channel = region_array[:, :, 1] / 255.0  
                b_channel = region_array[:, :, 2] / 255.0
                
                luma_bt709 = 0.2126 * r_channel + 0.7152 * g_channel + 0.0722 * b_channel
                
                # Store luma data
                all_luma_data.extend(luma_bt709.flatten())
                
            except Exception as e:
                print(f"Warning: Could not extract region {x1,y1,x2,y2}: {e}")
                continue
        
        # Convert to numpy array
        if not all_luma_data:
            raise Exception("No valid regions captured")
        
        luma_array = np.array(all_luma_data)
        
        # Calculate overall luma
        luma = np.mean(luma_array)
        
        # Calculate contrast from luma
        contrast = np.std(luma_array)
        
        # Fast mode: simplified percentile calculation
        if FAST_MODE:
            # Use min/max instead of percentiles for speed
            min_luma = np.min(luma_array)
            max_luma = np.max(luma_array)
            highlight_ratio = np.sum(luma_array > 0.8) / luma_array.size
            median_luma = np.median(luma_array)
            shadow_ratio = np.sum(luma_array < 0.2) / luma_array.size
        else:
            # Original detailed analysis
            percentiles = np.percentile(luma_array, [1, 5, 10, 90, 95, 99])
            min_luma = percentiles[0]  # 1st percentile
            max_luma = percentiles[5]  # 99th percentile
            
            # Additional metrics for better analysis
            median_luma = np.median(luma_array)
            p5_luma = percentiles[1]  # 5th percentile
            p95_luma = percentiles[4] # 95th percentile
            
            # Calculate highlight ratio using luma
            high_luma_mask = luma_array > 0.8
            highlight_ratio = np.sum(high_luma_mask) / luma_array.size
            
            # Calculate shadow ratio for better scene analysis
            shadow_luma_mask = luma_array < 0.2
            shadow_ratio = np.sum(shadow_luma_mask) / luma_array.size
        
        return luma, contrast, min_luma, max_luma, highlight_ratio, median_luma, shadow_ratio
    except Exception as e:
        print(f"Error analyzing screen: {e}")
        return 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5

def calculate_targets(luma, contrast, min_luma, max_luma, highlight_ratio, median_luma, shadow_ratio):
    """Calculate optimal gamma, contrast, and brightness based on scene using custom settings"""
    global content_history, current_scene_type
    
    # Store current frame
    content_history.append((luma, contrast, min_luma, max_luma, highlight_ratio, median_luma, shadow_ratio))
    
    # Wait for enough frames
    if len(content_history) < 3:
        return 1.0, 1.0, 1.0
    
    # Calculate averages
    recent_data = list(content_history)[-3:]
    avg_luma = np.mean([d[0] for d in recent_data])
    avg_min = np.mean([d[2] for d in recent_data])
    avg_max = np.mean([d[3] for d in recent_data])
    avg_highlight_ratio = np.mean([d[4] for d in recent_data])
    
    # Determine scene type
    current_scene_type = get_scene_type(avg_luma, avg_highlight_ratio)
    
    # Use custom settings for this scene type
    scene_settings = custom_settings[current_scene_type]
    target_gamma = scene_settings["gamma"]
    target_contrast = scene_settings["contrast"]
    target_brightness = scene_settings["brightness"]
    
    return target_gamma, target_contrast, target_brightness

def check_screen_luma():
    """Continuous check of screen luma without gamma adjustments"""
    print(f"\n=== CONTINUOUS SCREEN LUMA CHECK ===")
    
    # Get current screen resolution dynamically
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    
    print(f"Analyzing {screen_width}x{screen_height} screen every {REFRESH_RATE*1000:.0f}ms")
    print("Press Ctrl+C to stop\n")
    
    try:
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        
        frame_count = 0
        
        while running:
            # Capture area excluding top and bottom 150px (as percentage of screen)
            margin = int(0.1 * screen_height)  # 10% margin
            bbox = (0, margin, screen_width, screen_height - margin)
            screen = ImageGrab.grab(bbox=bbox).convert('RGB')
            img_array = np.array(screen)
            
            # Calculate proper luma from RGB using multiple methods for accuracy
            # Method 1: ITU-R BT.709 standard (most accurate for video)
            r_channel = img_array[:, :, 0] / 255.0
            g_channel = img_array[:, :, 1] / 255.0  
            b_channel = img_array[:, :, 2] / 255.0
            
            # BT.709 luma: 0.2126*R + 0.7152*G + 0.0722*B
            luma_bt709 = 0.2126 * r_channel + 0.7152 * g_channel + 0.0722 * b_channel
            
            # Use BT.709 as primary (most accurate for video content)
            luma_array = luma_bt709
            luma = np.mean(luma_array)
            
            # No scaling factor - BT.709 should give correct 0-1 range directly
            
            # Calculate min/max for range analysis using luma
            percentiles = np.percentile(luma_array, [1, 5, 10, 90, 95, 99])
            min_luma = percentiles[0]  # 1st percentile
            max_luma = percentiles[5]  # 99th percentile
            
            # Additional metrics for better analysis
            median_luma = np.median(luma_array)
            p5_luma = percentiles[1]  # 5th percentile
            p95_luma = percentiles[4] # 95th percentile
            
            # Calculate highlight ratio using luma
            high_luma_mask = luma_array > 0.8
            highlight_ratio = np.sum(high_luma_mask) / luma_array.size
            
            # Calculate shadow ratio for better scene analysis
            shadow_luma_mask = luma_array < 0.2
            shadow_ratio = np.sum(shadow_luma_mask) / luma_array.size
            
            # Debug output every second
            if frame_count % int(1.0 / REFRESH_RATE) == 0:  # Every 1 second
                # Quick debug - show raw pixel values when luma is very low
                raw_mean = np.mean(img_array)
                raw_max = np.max(img_array)
                raw_min = np.min(img_array)
                
                if luma < 0.1:  # Very low luma - show debug info
                    print(f"Luma: {luma:.3f} | Raw: {raw_mean:.1f} (min:{raw_min:.1f} max:{raw_max:.1f}) | Shape: {img_array.shape}", flush=True)
                else:
                    print(f"Luma: {luma:.3f}", flush=True)  # Normal luma printing
            
            # Determine scene type
            if highlight_ratio > 0.8:
                scene_type = "VERY BRIGHT"
            elif luma < DARK_THRESHOLD:
                scene_type = "VERY DARK"
            elif luma < LOWER_DARK_THRESHOLD:
                scene_type = "LOWER DARK"
            elif luma < MID_DARK_THRESHOLD:
                scene_type = "MID DARK"
            elif luma < UPPER_DARK_THRESHOLD:
                scene_type = "UPPER DARK"
            elif luma < LOWER_MID_THRESHOLD:
                scene_type = "LOWER-MID"
            elif luma < MID_THRESHOLD:
                scene_type = "MID"
            elif luma < UPPER_MID_THRESHOLD:
                scene_type = "UPPER-MID"
            else:
                scene_type = "BRIGHT"
            
            # Status update every second
            frame_count += 1
            if frame_count % int(1.0 / REFRESH_RATE) == 0:
                print(f"Luma Check | {scene_type} | Luma: {luma:.3f} | Min: {min_luma:.3f} | Max: {max_luma:.3f} | Highlights: {highlight_ratio:.2f}", end='\r')
            
            time.sleep(REFRESH_RATE)
            
    except KeyboardInterrupt:
        print(f"\n\nLuma check stopped.")
    except Exception as e:
        print(f"\n\nError: {e}")

def cleanup():
    """Restore default settings"""
    global running
    running = False
    print("\nRestoring default settings...")
    if apply_settings(1.0, 1.0):
        print("Settings restored successfully!")
    else:
        print("Warning: Could not restore settings")

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

def main():
    global current_gamma, current_contrast, current_brightness, running
    
    # Load custom settings at startup
    load_custom_settings()
    # Load configuration at startup
    load_config()
    
    while True:
        show_menu()
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            # Start ScreenBooster with keyboard controls
            print("\nStarting ScreenBooster with keyboard controls...")
            print("Press Ctrl+C to stop")
            run_screenbooster()
        elif choice == "2":
            config_menu()
        elif choice == "3":
            scene_menu()
        elif choice == "4":
            view_current_settings()
        elif choice == "5":
            check_screen_luma()
        elif choice == "6":
            reset_all_defaults()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def run_screenbooster():
    """Run the main ScreenBooster functionality"""
    global current_gamma, current_contrast, current_brightness, running
    
    print("\nScreenBooster - Clean Hardware Gamma & Contrast Control")
    print("Multi-area screen analysis with smooth transitions")
    
    # Get current screen resolution dynamically
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    
    print(f"Analysis: 15 sample areas every {REFRESH_RATE*1000:.0f}ms")
    print(f"Screen resolution: {screen_width}x{screen_height}")
    print(f"Smoothing: {SMOOTHING} (0.05=slow, 0.9=fast)")
    
    # Start keyboard listener in a separate thread
    keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
    keyboard_thread.start()
    
    try:
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        
        frame_count = 0
        
        while running:
            # Analyze screen
            luma, contrast, min_luma, max_luma, highlight_ratio, median_luma, shadow_ratio = analyze_screen()
            
            # Calculate targets using custom settings
            target_gamma, target_contrast, target_brightness = calculate_targets(luma, contrast, min_luma, max_luma, highlight_ratio, median_luma, shadow_ratio)
            
            # Smooth transitions
            current_gamma += (target_gamma - current_gamma) * SMOOTHING
            current_contrast += (target_contrast - current_contrast) * SMOOTHING
            current_brightness += (target_brightness - current_brightness) * SMOOTHING
            
            # Apply settings
            if apply_settings(current_gamma, current_contrast, current_brightness):
                frame_count += 1
                
                # Status update every second
                if frame_count % int(1.0 / REFRESH_RATE) == 0:
                    scene_type = current_scene_type
                    custom_vals = custom_settings[scene_type]
                    gamma_change = target_gamma - current_gamma
                    contrast_change = target_contrast - current_contrast
                    brightness_change = target_brightness - current_brightness
                    print(f"{scene_type} | γ{current_gamma:.2f} C{current_contrast:.2f} B{current_brightness:.2f} | Custom: γ{custom_vals['gamma']:.2f} C{custom_vals['contrast']:.2f} B{custom_vals['brightness']:.2f} | Δγ{gamma_change:+.2f} ΔC{contrast_change:+.2f} ΔB{brightness_change:+.2f} | Luma: {luma:.3f}", end='\r')
            
            time.sleep(REFRESH_RATE)
            
    except KeyboardInterrupt:
        print(f"\n\nStopping adjustments...")
    except Exception as e:
        print(f"\n\nError: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
