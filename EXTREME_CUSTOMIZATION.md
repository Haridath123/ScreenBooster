# ScreenBooster V4 - Extreme Customization Guide

## 🎯 Introduction to Advanced Configuration

This guide provides detailed instructions for manually editing ScreenBooster's parameters and profiles for ultimate customization. Whether you want to fine-tune performance, create custom scenes, or build entirely new profiles, this guide covers everything.

## 📁 File Structure Overview

```
ScreenBooster/
├── main.py                    # Core application & performance parameters
├── screenbooster_profiles.json # Scene-specific gamma/contrast/brightness values
├── screenbooster_config.json  # Global configuration & thresholds
└── requirements.txt           # Python dependencies (not for editing)
```

## 🔧 Editing main.py - Core Parameters

### **⚠️ IMPORTANT: Backup First!**
Before editing main.py, always create a backup:
```bash
copy main.py main.py.backup
```

### **🎛️ Performance & Behavior Parameters**

Find these parameters in `main.py` (lines 16-68):

#### **1. Smoothing & Responsiveness**
```python
SMOOTHING = 0.1          # Transition speed (0.05-0.9)
REFRESH_RATE = 0.03       # Analysis interval in seconds (0.001-0.1)
CONTENT_HISTORY_SIZE = 3 # Frames to analyze (1-10)
```

**SMOOTHING Details:**
- `0.05` = Ultra-smooth, slow transitions (good for movies)
- `0.1` = Balanced (default, good for most use)
- `0.3` = Fast transitions (good for gaming)
- `0.9` = Instant changes (may be jarring)

**REFRESH_RATE Details:**
- `0.001` = 1000Hz analysis (extremely responsive, high CPU)
- `0.01` = 100Hz analysis (very responsive, moderate CPU)
- `0.03` = 33Hz analysis (default, balanced)
- `0.1` = 10Hz analysis (low CPU, slower response)

#### **2. Scene Detection Thresholds**
```python
# 23 total thresholds for precise scene classification
VERY_DARK_THRESHOLD = 0.00      # Below this = very dark scene
DARK_THRESHOLD = 0.04             # Dark scene
LOWER_DARK_THRESHOLD = 0.08       # Lower dark scene
MID_DARK_THRESHOLD = 0.12        # Mid dark scene
UPPER_DARK_THRESHOLD = 0.16       # Upper dark scene
# ... continues through all 23 thresholds
BRIGHT_THRESHOLD = 0.84            # Above this = bright scene
```

**Customizing Thresholds:**
- Values must be in ascending order (0.00 to 1.00)
- Smaller gaps = more scene categories, more precise adjustments
- Larger gaps = fewer scene changes, more stable experience
- Example for aggressive dark detection:
  ```python
  DARK_THRESHOLD = 0.08           # Move from 0.04 to 0.08
  LOWER_DARK_THRESHOLD = 0.15     # Move from 0.08 to 0.15
  ```

#### **3. Performance Optimization**
```python
SKIP_FRAMES = 2           # Skip every N frames for analysis (0-10)
FAST_MODE = True          # Enable fast mode optimizations
REGION_SAMPLE_SIZE = 0.05 # Sample smaller regions (0.01-0.1)
```

**Performance Tuning:**
- `SKIP_FRAMES = 0`: Analyze every frame (most accurate, highest CPU)
- `SKIP_FRAMES = 2`: Analyze every 3rd frame (default, balanced)
- `SKIP_FRAMES = 5`: Analyze every 6th frame (low CPU)
- `REGION_SAMPLE_SIZE = 0.01`: Tiny samples (fastest, less accurate)
- `REGION_SAMPLE_SIZE = 0.1`: Large samples (slowest, most accurate)

#### **4. Safety & Control**
```python
safety_lock_enabled = True  # Default to locked (True/False)
safety_key_combination = "ctrl+alt"  # Safety unlock combination
SAFETY_COOLDOWN = 0.1  # Seconds between safety checks (0.01-1.0)
```

**Safety Customization:**
- Set `safety_lock_enabled = False` to disable safety lock entirely
- Change `safety_key_combination` to any keyboard combo
- Increase `SAFETY_COOLDOWN` for less frequent checks (better performance)

#### **5. Adjustment Step Sizes**
```python
GAMMA_STEP = 0.1        # Gamma adjustment increment (0.01-0.5)
CONTRAST_STEP = 0.05    # Contrast adjustment increment (0.01-0.2)
BRIGHTNESS_STEP = 0.05  # Brightness adjustment increment (0.01-0.2)
```

**Fine-tuning Steps:**
- Smaller values = more precise control
- Larger values = faster adjustments
- Example for ultra-fine control:
  ```python
  GAMMA_STEP = 0.01
  CONTRAST_STEP = 0.005
  BRIGHTNESS_STEP = 0.005
  ```

## 🎨 Editing screenbooster_profiles.json - Scene Profiles

### **⚠️ IMPORTANT: JSON Format is Strict!**
JSON files require exact formatting:
- No trailing commas
- All strings in double quotes
- All brackets/braces properly paired
- Use a JSON validator if unsure

### **📊 Profile Structure Overview**
```json
{
  "game": {
    "SCENE_NAME": {
      "gamma": 1.0,
      "contrast": 1.0, 
      "brightness": 1.0
    }
  },
  "movie": {
    "SCENE_NAME": {
      "gamma": 1.0,
      "contrast": 1.0,
      "brightness": 1.0
    }
  },
  "current_profile": "game"
}
```

### **🎬 Understanding Parameter Ranges**

#### **Gamma (γ): Brightness Curve**
- **Range:** 0.1 to 10.0
- **1.0** = Normal/neutral
- **< 1.0** = Darker image, crushed blacks
- **> 1.0** = Brighter image, lifted shadows
- **Usage Examples:**
  - `0.5`: Very dark, high contrast (artistic)
  - `1.0`: Normal display
  - `2.0`: Brightened shadows
  - `5.0`: Extreme shadow boost (for very dark scenes)
  - `10.0`: Maximum brightness (may wash out)

#### **Contrast (C): Detail Enhancement**
- **Range:** 0.1 to 3.0
- **1.0** = Normal/neutral
- **< 1.0** = Lower contrast, flatter image
- **> 1.0** = Higher contrast, more detail
- **Usage Examples:**
  - `0.5`: Low contrast, soft look
  - `1.0`: Normal contrast
  - `1.5`: Enhanced contrast, more pop
  - `2.0`: High contrast, dramatic look
  - `3.0`: Maximum contrast (may lose detail)

#### **Brightness (B): Overall Luminance**
- **Range:** 0.1 to 2.0
- **1.0** = Normal/neutral
- **< 1.0** = Dimmer overall
- **> 1.0** = Brighter overall
- **Usage Examples:**
  - `0.7`: Dim, comfortable for dark rooms
  - `1.0`: Normal brightness
  - `1.2**: Bright, good for well-lit rooms
  - `1.5`: Very bright, for high ambient light
  - `2.0`: Maximum brightness (may cause eye strain)

### **🎮 Complete Scene List & Customization**

#### **23 Scene Types (from darkest to brightest):**
1. `VERY_DARK` - Almost black content
2. `DARK` - Very dark scenes
3. `LOWER_DARK` - Dark scenes
4. `MID_DARK` - Moderately dark
5. `UPPER_DARK` - Slightly dark
6. `LOWER_MID_DARK` - Dark-mid transition
7. `MID_MID_DARK` - Mid-dark
8. `UPPER_MID_DARK` - Upper-mid dark
9. `LOWER_MID` - Lower mid-range
10. `MID_LOWER_MID` - Mid-lower
11. `UPPER_LOWER_MID` - Upper-lower mid
12. `MID` - True mid-range
13. `LOWER_UPPER_MID` - Lower-upper mid
14. `MID_UPPER_MID` - Mid-upper mid
15. `UPPER_MID` - Upper mid-range
16. `LOWER_BRIGHT_MID` - Lower-bright mid
17. `MID_BRIGHT_MID` - Mid-bright mid
18. `UPPER_BRIGHT_MID` - Upper-bright mid
19. `LOWER_BRIGHT` - Lower bright
20. `MID_BRIGHT` - Mid bright
21. `UPPER_BRIGHT` - Upper bright
22. `BRIGHT` - Bright scenes
23. `VERY_BRIGHT` - Very bright content

### **🎯 Profile Customization Examples**

#### **Example 1: Competitive Gaming Profile**
```json
{
  "game": {
    "VERY_DARK": {"gamma": 8.0, "contrast": 3.0, "brightness": 1.2},
    "DARK": {"gamma": 6.0, "contrast": 2.5, "brightness": 1.1},
    "LOWER_DARK": {"gamma": 4.0, "contrast": 2.0, "brightness": 1.0},
    "MID_DARK": {"gamma": 2.5, "contrast": 1.5, "brightness": 1.0},
    "UPPER_DARK": {"gamma": 1.5, "contrast": 1.2, "brightness": 1.0},
    "LOWER_MID_DARK": {"gamma": 1.2, "contrast": 1.1, "brightness": 1.0},
    "MID_MID_DARK": {"gamma": 1.1, "contrast": 1.0, "brightness": 1.0},
    "UPPER_MID_DARK": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_LOWER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_LOWER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "VERY_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0}
  }
}
```

#### **Example 2: Cinematic Movie Profile**
```json
{
  "movie": {
    "VERY_DARK": {"gamma": 4.0, "contrast": 1.8, "brightness": 1.3},
    "DARK": {"gamma": 3.0, "contrast": 1.6, "brightness": 1.2},
    "LOWER_DARK": {"gamma": 2.2, "contrast": 1.4, "brightness": 1.1},
    "MID_DARK": {"gamma": 1.6, "contrast": 1.2, "brightness": 1.0},
    "UPPER_DARK": {"gamma": 1.3, "contrast": 1.1, "brightness": 1.0},
    "LOWER_MID_DARK": {"gamma": 1.2, "contrast": 1.05, "brightness": 1.0},
    "MID_MID_DARK": {"gamma": 1.1, "contrast": 1.02, "brightness": 1.0},
    "UPPER_MID_DARK": {"gamma": 1.05, "contrast": 1.01, "brightness": 1.0},
    "LOWER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_LOWER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_LOWER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 0.95},
    "MID_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 0.95},
    "UPPER_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 0.95},
    "LOWER_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 0.95},
    "MID_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 0.95},
    "UPPER_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 0.95},
    "BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 0.95},
    "VERY_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 0.95}
  }
}
```

#### **Example 3: Productivity/Reading Profile**
```json
{
  "productivity": {
    "VERY_DARK": {"gamma": 2.0, "contrast": 1.3, "brightness": 1.1},
    "DARK": {"gamma": 1.5, "contrast": 1.2, "brightness": 1.05},
    "LOWER_DARK": {"gamma": 1.3, "contrast": 1.1, "brightness": 1.02},
    "MID_DARK": {"gamma": 1.2, "contrast": 1.05, "brightness": 1.0},
    "UPPER_DARK": {"gamma": 1.1, "contrast": 1.02, "brightness": 1.0},
    "LOWER_MID_DARK": {"gamma": 1.05, "contrast": 1.01, "brightness": 1.0},
    "MID_MID_DARK": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_MID_DARK": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_LOWER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_LOWER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_BRIGHT_MID": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "LOWER_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "MID_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "UPPER_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0},
    "VERY_BRIGHT": {"gamma": 1.0, "contrast": 1.0, "brightness": 1.0}
  }
}
```

## 🔧 Editing screenbooster_config.json - Global Settings

### **Configuration Structure:**
```json
{
  "SMOOTHING": 0.1,
  "REFRESH_RATE": 0.03,
  "CONTENT_HISTORY_SIZE": 3,
  "FAST_MODE": true,
  "SKIP_FRAMES": 2,
  "DARK_THRESHOLD": 0.04,
  "LOWER_DARK_THRESHOLD": 0.08,
  "MID_DARK_THRESHOLD": 0.12,
  "UPPER_DIDARK_THRESHOLD": 0.16,
  "LOWER_MID_THRESHOLD": 0.32,
  "MID_THRESHOLD": 0.44,
  "UPPER_MID_THRESHOLD": 0.56,
  "BRIGHT_THRESHOLD": 0.84
}
```

### **When to Edit Config vs Main.py:**
- **Config file:** For user-facing adjustments (performance, thresholds)
- **Main.py:** For developer-level changes (safety, step sizes, new features)

## 🎯 Advanced Customization Techniques

### **1. Creating Custom Profiles**
1. Copy existing profile structure
2. Rename profile (e.g., "game" → "fps")
3. Adjust values for specific use case
4. Update `current_profile` to new profile name
5. Add profile switching logic in main.py if needed

### **2. Fine-Tuning Scene Transitions**
For smoother transitions between specific scenes:
```json
{
  "MID_DARK": {"gamma": 1.8, "contrast": 1.3, "brightness": 1.0},
  "UPPER_DARK": {"gamma": 1.6, "contrast": 1.2, "brightness": 1.0},
  "LOWER_MID_DARK": {"gamma": 1.4, "contrast": 1.1, "brightness": 1.0}
}
```
Notice the gradual progression: 1.8 → 1.6 → 1.4

### **3. Extreme Performance Tuning**
For low-end systems:
```python
# In main.py
REFRESH_RATE = 0.1        # 10Hz analysis
SKIP_FRAMES = 5           # Analyze every 6th frame
FAST_MODE = True
REGION_SAMPLE_SIZE = 0.01 # Smallest samples
```

### **4. Quality-First Tuning**
For high-end systems:
```python
# In main.py
REFRESH_RATE = 0.005      # 200Hz analysis
SKIP_FRAMES = 0           # Analyze every frame
FAST_MODE = False
REGION_SAMPLE_SIZE = 0.1  # Largest samples
```

## 🧪 Testing & Validation

### **1. Parameter Validation**
Before using custom values, test them:
1. Start with conservative changes
2. Test with various content types
3. Monitor CPU usage and performance
4. Check for visual artifacts or flickering

### **2. Profile Testing**
1. Create test content with different brightness levels
2. Verify smooth transitions between scenes
3. Check that extreme values don't cause washout
4. Ensure safety features still work

### **3. Performance Testing**
1. Monitor CPU usage during operation
2. Test with different refresh rates
3. Verify frame skipping doesn't cause stuttering
4. Check memory usage remains reasonable

## 🚨 Troubleshooting Custom Configurations

### **Common Issues & Solutions:**

#### **JSON Syntax Errors**
**Problem:** Invalid JSON format
**Solution:** Use online JSON validator, check for:
- Missing commas
- Trailing commas
- Unmatched brackets/braces
- Single quotes instead of double quotes

#### **Parameter Range Errors**
**Problem:** Values outside acceptable ranges
**Solution:** Check ranges:
- Gamma: 0.1-10.0
- Contrast: 0.1-3.0
- Brightness: 0.1-2.0
- Thresholds: 0.0-1.0 (ascending order)

#### **Performance Issues**
**Problem:** High CPU usage or lag
**Solution:** Adjust performance parameters:
- Increase REFRESH_RATE
- Increase SKIP_FRAMES
- Enable FAST_MODE
- Reduce REGION_SAMPLE_SIZE

#### **Visual Artifacts**
**Problem:** Flickering or jarring changes
**Solution:** Adjust smoothing:
- Increase SMOOTHING value
- Check for large parameter jumps between scenes
- Verify threshold values create smooth transitions

## 🎯 Best Practices

### **1. Incremental Changes**
- Make small adjustments one at a time
- Test each change before proceeding
- Keep backups of working configurations

### **2. Documentation**
- Document your custom values
- Note why specific changes were made
- Keep track of what works best for your use case

### **3. Testing Environments**
- Test with different content types (games, movies, desktop)
- Verify performance under different system loads
- Check compatibility with different monitor types

### **4. Safety Considerations**
- Never disable safety features permanently
- Keep values within recommended ranges
- Test extreme values carefully

## 📚 Reference Tables

### **Quick Reference: Parameter Effects**

| Parameter | Low Value | High Value | Recommended Range |
|-----------|-----------|------------|-------------------|
| Gamma | Darker, crushed blacks | Brighter, washed out | 0.5-3.0 |
| Contrast | Flat, low detail | High contrast, dramatic | 0.8-2.0 |
| Brightness | Dim, comfortable | Bright, may cause strain | 0.7-1.3 |
| Smoothing | Slow, smooth | Fast, jarring | 0.05-0.3 |
| Refresh Rate | Low CPU, slow response | High CPU, instant response | 0.01-0.1 |

### **Scene-Specific Recommendations**

| Scene Type | Gamma Range | Contrast Range | Use Case |
|------------|-------------|----------------|----------|
| VERY_DARK | 3.0-8.0 | 1.5-3.0 | Horror games, dark movies |
| DARK | 2.0-5.0 | 1.3-2.5 | Night scenes, caves |
| MID | 0.8-1.5 | 1.0-1.5 | Normal indoor lighting |
| BRIGHT | 0.8-1.2 | 1.0-1.3 | Daylight, outdoor scenes |
| VERY_BRIGHT | 0.8-1.1 | 1.0-1.2 | Snow, bright environments |

---

## 🔚 Conclusion

This guide provides everything needed for extreme customization of ScreenBooster V4. Whether you're fine-tuning for competitive gaming, cinematic experiences, or productivity work, these parameters give you complete control over the auto-exposure system.

**Remember:** With great power comes great responsibility. Always test changes carefully and keep backups of working configurations.

**Happy customizing!** 🎮🎬🖥️
