import ctypes
import numpy as np
from PIL import ImageGrab, Image
import time
import sys
import os
import threading
import keyboard

# Hardware access
gdi32 = ctypes.WinDLL('gdi32')
user32 = ctypes.windll.user32

# Configuration
REFRESH_RATE = 0.0001  # Screen analysis interval (seconds)
SMOOTHING = 0.3       # Transition speed (0.05-0.9) - lower = smoother
ANALYSIS_RESOLUTION = (384, 216)  # Downscale for performance

# Luma thresholds and corresponding gamma/contrast/brightness values
# luma ≥ 100/255 (0.392): no boost
# 70/255 ≤ luma < 100/255: gamma 1.4, brightness 1, contrast 1.1
# 50/255 ≤ luma < 70/255: gamma 1.8, brightness 1, contrast 1.3
# 35/255 ≤ luma < 50/255: gamma 2.0, brightness 1, contrast 1.4
# 25/255 ≤ luma < 35/255: gamma 2.4, brightness 1, contrast 1.6
# 15/255 ≤ luma < 25/255: gamma 2.7, brightness 1, contrast 1.8
# luma < 15/255: gamma 2.7, brightness 1, contrast 1.8

LUMA_THRESHOLDS = [
    (0.392, 0.99, 0.99, 1.0),    # ≥ 100/255: no boost
    (0.275, 1.4, 0.99, 1.1),    # 70/255 ≤ luma < 100/255
    (0.196, 1.8, 0.99, 1.3),    # 50/255 ≤ luma < 70/255
    (0.137, 2.0, 0.99, 1.4),    # 35/255 ≤ luma < 50/255
    (0.098, 2.4, 0.99, 1.6),    # 25/255 ≤ luma < 35/255
    (0.059, 2.7, 0.99, 1.8),    # 15/255 ≤ luma < 25/255
    (0.0,   2.7, 0.99, 1.8),    # < 15/255
]

# Current state
current_gamma = 1.0
current_contrast = 1.0
current_brightness = 1.0
running = True

def check_admin_privileges():
    """Check if running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def apply_settings(gamma, contrast, brightness=1.0):
    """Apply hardware gamma, contrast, and brightness adjustments to all monitors"""
    try:
        ramp = (ctypes.c_ushort * 768)()
        
        for i in range(256):
            n = i / 255.0
            
            # Apply brightness first
            n = n * brightness
            
            # Apply gamma
            gamma_corrected = n ** (1.0 / gamma)
            
            # Apply contrast
            if contrast != 1.0:
                if contrast > 1.0:
                    contrast_adjusted = (gamma_corrected - 0.5) * contrast + 0.5
                    gamma_corrected = max(0.0, min(1.0, contrast_adjusted))
                    
                    if gamma_corrected > 0.7:
                        highlight_boost = (gamma_corrected - 0.7) * 0.2
                        gamma_corrected = min(1.0, gamma_corrected + highlight_boost)
                else:
                    contrast_adjusted = (gamma_corrected - 0.5) * contrast + 0.5
                    gamma_corrected = max(0.0, min(1.0, contrast_adjusted))
            
            # Convert to 16-bit for hardware
            res = int(gamma_corrected * 65535.0)
            ramp[i] = ramp[i + 256] = ramp[i + 512] = res
        
        # Store monitor device names
        monitor_devices = []
        
        # Callback to enumerate display devices
        def monitor_callback(hmonitor, hdc, rect, data):
            monitor_info = ctypes.create_string_buffer(104)  # MONITORINFOEX size
            ctypes.memset(monitor_info, 0, 104)
            monitor_info_raw = ctypes.cast(monitor_info, ctypes.POINTER(ctypes.c_int))
            monitor_info_raw[0] = 104  # cbSize
            
            if user32.GetMonitorInfoW(hmonitor, monitor_info):
                # Extract device name from MONITORINFOEX (offset 40)
                device_name = ctypes.wstring_at(ctypes.addressof(monitor_info) + 40)
                monitor_devices.append(device_name)
            return 1
        
        # Define callback type
        MONITORENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.c_int), ctypes.c_ulong)
        
        # Enumerate all monitors
        user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(monitor_callback), 0)
        
        # Apply gamma ramp to each monitor device
        success_count = 0
        for device_name in monitor_devices:
            try:
                hdc = gdi32.CreateDCW(device_name, None, None, None)
                if hdc:
                    result = gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(ramp))
                    gdi32.DeleteDC(hdc)
                    if result:
                        success_count += 1
            except Exception as e:
                print(f"Error applying to {device_name}: {e}")
        
        # Also apply to primary DC as fallback
        hdc = user32.GetDC(None)
        gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(ramp))
        user32.ReleaseDC(None, hdc)
        
        return success_count > 0
    except Exception as e:
        print(f"Error applying display settings: {e}")
        return False

def calculate_luma(image):
    """Calculate luma using equal channel weighting"""
    img_array = np.array(image)
    r_channel = img_array[:, :, 0] / 255.0
    g_channel = img_array[:, :, 1] / 255.0
    b_channel = img_array[:, :, 2] / 255.0
    
    luma_equal = (r_channel + g_channel + b_channel) / 3.0
    return np.mean(luma_equal)

def get_target_settings(luma):
    """Get target gamma, contrast, brightness based on luma"""
    for threshold, gamma, brightness, contrast in LUMA_THRESHOLDS:
        if luma >= threshold:
            return gamma, contrast, brightness
    return 2.7, 1.8, 1.0  # Fallback for very dark

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
    
    # Check for administrator privileges
    if not check_admin_privileges():
        print("\n" + "="*60)
        print("⚠️  WARNING: NOT RUNNING AS ADMINISTRATOR")
        print("="*60)
        print("\nThis app requires Administrator privileges to modify")
        print("display settings. Without admin rights, the screen adjustments")
        print("will not work on most Windows systems.")
        print("\n" + "="*60)
        print("\nContinuing anyway (adjustments will likely fail)...\n")
        time.sleep(2)
    
    print("Simple Luma Booster")
    print("Press Ctrl+C to stop\n")
    
    try:
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        
        # Get primary monitor resolution
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        print(f"Screen resolution: {screen_width}x{screen_height}")
        print(f"Analysis: Full screen every {REFRESH_RATE*1000:.0f}ms")
        print(f"Smoothing: {SMOOTHING} (lower = smoother transitions)\n")
        
        while running:
            # Capture screen (ImageGrab.grab() without bbox captures primary monitor)
            full_screen = ImageGrab.grab().convert('RGB')
            analysis_screen = full_screen.resize(ANALYSIS_RESOLUTION, Image.LANCZOS)
            
            # Calculate luma
            luma = calculate_luma(analysis_screen)
            
            # Get target settings based on luma
            target_gamma, target_contrast, target_brightness = get_target_settings(luma)
            
            # Smooth transitions
            current_gamma += (target_gamma - current_gamma) * SMOOTHING
            current_contrast += (target_contrast - current_contrast) * SMOOTHING
            current_brightness += (target_brightness - current_brightness) * SMOOTHING
            
            # Apply settings
            apply_settings(current_gamma, current_contrast, current_brightness)
            
            # Display
            luma_255 = luma * 255
            print(f"\rLuma: {luma_255:.0f}      Adjusted: γ{current_gamma:.2f} C{current_contrast:.2f} B{current_brightness:.2f}", end="", flush=True)
            
            time.sleep(REFRESH_RATE)
            
    except KeyboardInterrupt:
        print(f"\n\nStopping adjustments...")
    except Exception as e:
        print(f"\n\nError: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
