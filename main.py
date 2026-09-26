import ctypes
import numpy as np
from PIL import ImageGrab
import time
import sys
from collections import deque

# Hardware access
gdi32 = ctypes.WinDLL('gdi32')
user32 = ctypes.windll.user32

# Configuration
SMOOTHING = 0.1          # Transition speed (0.05-0.9) - reduced for smoother transitions
REFRESH_RATE = 0.01       # Screen analysis interval (seconds)
CONTENT_HISTORY_SIZE = 3 # Frames to analyze

# Scene thresholds
DARK_THRESHOLD = 0.05      # Below this = very dark scene
LOWER_DARK_THRESHOLD = 0.10  # Lower dark scene
MID_DARK_THRESHOLD = 0.20    # Mid dark scene
UPPER_DARK_THRESHOLD = 0.30   # Upper dark scene
LOWER_MID_THRESHOLD = 0.45  # Lower-mid scene  
MID_THRESHOLD = 0.50       # True mid scene
UPPER_MID_THRESHOLD = 0.65  # Upper-mid scene
BRIGHT_THRESHOLD = 0.85   # Above this = bright scene

# Current state
current_gamma = 1.0
current_contrast = 1.0
current_brightness = 1.0
content_history = deque(maxlen=CONTENT_HISTORY_SIZE)
running = True

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
    """Analyze multiple screen areas (center, corners, in-between) for brightness and contrast"""
    try:
        # Capture entire screen once, then extract regions
        screen_width, screen_height = 1920, 1080
        
        # Single full screen capture
        full_screen = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height)).convert('RGB')
        full_array = np.array(full_screen)
        
        # Define sample areas: (x1, y1, x2, y2) - center is 200x200, others are 100x100
        sample_areas = [
            # Center (bigger - most important area)
            (screen_width//2 - 100, screen_height//2 - 100, screen_width//2 + 100, screen_height//2 + 100),
            
            # Corners (100x100)
            (25, 25, 125, 125),                    # Top-left
            (screen_width - 125, 25, screen_width - 25, 125),  # Top-right
            (25, screen_height - 125, 125, screen_height - 25),  # Bottom-left
            (screen_width - 125, screen_height - 125, screen_width - 25, screen_height - 25),  # Bottom-right
            
            # Mid-edges (100x100)
            (screen_width//2 - 50, 25, screen_width//2 + 50, 125),  # Top-center
            (screen_width//2 - 50, screen_height - 125, screen_width//2 + 50, screen_height - 25),  # Bottom-center
            (25, screen_height//2 - 50, 125, screen_height//2 + 50),  # Left-center
            (screen_width - 125, screen_height//2 - 50, screen_width - 25, screen_height//2 + 50),  # Right-center
            
            # Center-left and center-right (100x100)
            (screen_width//3 - 50, screen_height//2 - 50, screen_width//3 + 50, screen_height//2 + 50),  # Center-left
            (2*screen_width//3 - 50, screen_height//2 - 50, 2*screen_width//3 + 50, screen_height//2 + 50),  # Center-right
            
            # In-between diagonal points (100x100)
            (screen_width//4 - 25, screen_height//4 - 25, screen_width//4 + 25, screen_height//4 + 25),  # Top-left quadrant
            (3*screen_width//4 - 25, screen_height//4 - 25, 3*screen_width//4 + 25, screen_height//4 + 25),  # Top-right quadrant
            (screen_width//4 - 25, 3*screen_height//4 - 25, screen_width//4 + 25, 3*screen_height//4 + 25),  # Bottom-left quadrant
            (3*screen_width//4 - 25, 3*screen_height//4 - 25, 3*screen_width//4 + 25, 3*screen_height//4 + 25),  # Bottom-right quadrant
        ]
        
        all_luma_data = []
        
        # Extract regions from the single full screen capture
        for x1, y1, x2, y2 in sample_areas:
            try:
                # Extract region from full screen array
                region_array = full_array[y1:y2, x1:x2]
                
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
        
        return luma, contrast, min_luma, max_luma, highlight_ratio, median_luma, shadow_ratio
    except Exception as e:
        print(f"Error analyzing screen: {e}")
        return 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5

def calculate_targets(luma, contrast, min_luma, max_luma, highlight_ratio, median_luma, shadow_ratio):
    """Calculate optimal gamma, contrast, and brightness based on scene"""
    global content_history
    
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
    
    # Determine scene type and calculate targets
    if avg_highlight_ratio > 0.8:
        target_gamma = 1.0
        target_contrast = 1.0
        target_brightness = 0.96
    elif avg_luma < DARK_THRESHOLD:
        # Very dark scene - make darker with gamma < 1.0
        target_gamma = 3.1 # Darker than 1.0 for deeper blacks
        target_contrast = 1.6 # Keep high contrast for deeper blacks
        target_brightness = 1.0 # Slightly brighter to lift darks
    elif avg_luma < LOWER_DARK_THRESHOLD:
        # Lower dark scene - moderate darkening
        target_gamma = 2.9 # Moderate darkening
        target_contrast = 1.9 # High contrast
        target_brightness = 0.9 # Slightly brighter
    elif avg_luma < MID_DARK_THRESHOLD:
        # Mid dark scene - slight darkening
        target_gamma = 2.6 # Slight darkening
        target_contrast = 1.8 # Moderate contrast
        target_brightness = 0.8 # Minimal brightness
    elif avg_luma < UPPER_DARK_THRESHOLD:
        # Upper dark scene - minimal darkening
        target_gamma = 2 # Minimal darkening
        target_contrast = 1.5 # Slight contrast boost
        target_brightness = 0.7 # No brightness change
    elif avg_luma < LOWER_MID_THRESHOLD:
        # Lower-mid scene - slight darkening
        target_gamma = 1.6 # Slightly darker than 1.0
        target_contrast = 1.3 # Slight contrast boost
        target_brightness = 0.9 # No brightness change
    elif avg_luma < MID_THRESHOLD:
        # True mid scene - minimal darkening
        target_gamma = 1.1 # Slightly darker than 1.0
        target_contrast = 1.1 # Minimal contrast boost
        target_brightness = 1.0 # No brightness change
    elif avg_luma < UPPER_MID_THRESHOLD:
        # Upper-mid scene - very minimal darkening
        target_gamma = 1.1 # Very slightly darker than 1.0
        target_contrast = 1.0 # Very slight contrast boost
        target_brightness = 1.0 # No brightness change
    else:
        # Bright scene - keep gamma unchanged, increase contrast for highlights
        target_gamma = 1.0   # Keep gamma at standard
        target_contrast = 1.0  # Give bright scenes proper contrast boost
        target_brightness = 1.0  # No brightness change for bright scenes
    
    # NO RANGE OPTIMIZATION - Use settings as intended
    return target_gamma, target_contrast, target_brightness

def check_screen_luma():
    """Continuous check of screen luma without gamma adjustments"""
    print(f"\n=== CONTINUOUS SCREEN LUMA CHECK ===")
    print(f"Analyzing 1920x800 center area every {REFRESH_RATE*1000:.0f}ms")
    print("Press Ctrl+C to stop\n")
    
    try:
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        
        frame_count = 0
        
        while running:
            # Capture area excluding top and bottom 150px
            bbox = (0, 150, 1920, 930)  # Full width, 150px margin top/bottom
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
    
    print("ScreenBooster - Clean Hardware Gamma & Contrast Control")
    print("Multi-area screen analysis (center, corners, edges, in-between) with smooth transitions")
    print(f"Analysis: 15 sample areas (center 200x200px, others 100x100px) every {REFRESH_RATE*1000:.0f}ms")
    print(f"Smoothing: {SMOOTHING} (0.05=slow, 0.9=fast)")
    print("\nOptions:")
    print("1. Run full gamma/contrast/brightness adjustment")
    print("2. Check current screen luma only")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "2":
        # Just check luma without running main program
        check_screen_luma()
        return
    elif choice == "3":
        return
    elif choice != "1":
        print("Invalid choice, running main program...")
    
    print("\nStarting gamma/contrast/brightness adjustment...")
    print("Press Ctrl+C to restore default settings and exit\n")
    
    try:
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        
        frame_count = 0
        
        while running:
            # Analyze screen
            luma, contrast, min_luma, max_luma, highlight_ratio, median_luma, shadow_ratio = analyze_screen()
            
            # Calculate targets
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
                    scene_type = "VERY BRIGHT" if highlight_ratio > 0.8 else "VERY DARK" if luma < DARK_THRESHOLD else "LOWER DARK" if luma < LOWER_DARK_THRESHOLD else "MID DARK" if luma < MID_DARK_THRESHOLD else "UPPER DARK" if luma < UPPER_DARK_THRESHOLD else "LOWER-MID" if luma < LOWER_MID_THRESHOLD else "MID" if luma < MID_THRESHOLD else "UPPER-MID" if luma < UPPER_MID_THRESHOLD else "BRIGHT"
                    gamma_change = target_gamma - current_gamma
                    contrast_change = target_contrast - current_contrast
                    brightness_change = target_brightness - current_brightness
                    print(f"{scene_type} | γ{current_gamma:.2f} C{current_contrast:.2f} B{current_brightness:.2f} | Target: γ{target_gamma:.2f} C{target_contrast:.2f} B{target_brightness:.2f} | Δγ{gamma_change:+.2f} ΔC{contrast_change:+.2f} ΔB{brightness_change:+.2f} | Luma: {luma:.3f}", end='\r')
            
            time.sleep(REFRESH_RATE)
            
    except KeyboardInterrupt:
        print(f"\n\nStopping adjustments...")
    except Exception as e:
        print(f"\n\nError: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
