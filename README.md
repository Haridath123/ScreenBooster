# ScreenBooster v2.2.0 - The Complete Auto-Exposure Journey

## 🎯 The Origin Story - Why This Exists

**The Problem:** Modern LCD monitors have incredible dynamic range capabilities, but most content - especially games and movies - doesn't utilize the full potential. Dark scenes often crush blacks into oblivion, while bright scenes could be more vibrant. I wanted a solution that would automatically optimize my screen's dynamic range in real-time, similar to how HDR works, but for standard SDR content.

**The Vision:** Create an intelligent auto-exposure system that:
- Makes dark scenes visible without washing them out
- Optimizes bright scenes for maximum impact  
- Adjusts smoothly and naturally in real-time
- Works with any content (games, movies, desktop)
- Requires no user intervention once configured

## 📚 The Evolution - 4 Versions of Trial and Error

### **ScreenBooster V1 - The Basic Concept**
**What it did:** Simple gamma adjustment based on average screen brightness
**Problems:**
- Flickering adjustments (jarring transitions)
- No scene intelligence (treated everything the same)
- Often over-brightened dark scenes
- No contrast optimization
- Basic 3-zone analysis

**Why it failed:** Too simplistic - screen content is complex and needs sophisticated analysis

### **ScreenBooster V2 - The Scene Detection Attempt**
**What it did:** Added basic scene detection (dark/mid/bright) with different gamma values
**Problems:**
- Scene detection was inaccurate (jumped between categories)
- Still no contrast adjustment
- Analysis was too slow (performance issues)
- No smoothing between transitions
- Limited to 5 screen regions

**Why it failed:** Better concept, but implementation was still too basic for real-world use

### **ScreenBooster V3 - The Advanced Algorithm**
**What it did:** 23-scene detection system with percentile analysis and contrast adjustment
**Problems:**
- Over-complicated (23 scenes was excessive)
- Percentile analysis was CPU intensive
- Settings were too aggressive for daily use
- No profile system (one-size-fits-all)
- Complex configuration confused users

**Why it failed:** Technically impressive but practically unusable - too complex and resource-heavy

### **ScreenBooster V4 - The Perfect Balance** ⭐
**What it does:** Intelligent 23-scene system with profile management, safety features, and smooth transitions
**Why it works:**
- **Smart Scene Detection:** 23 distinct scene types for precise adjustment
- **Profile System:** Separate settings for gaming vs movies
- **Safety Lock:** Prevents accidental adjustments while typing
- **Smooth Transitions:** Natural-feeling changes without jarring
- **Performance Optimized:** Fast analysis with minimal CPU usage
- **User-Friendly:** Simple menu system with live feedback

## 🧠 How ScreenBooster V4 Works - Technical Deep Dive

### **The Core Concept**
ScreenBooster analyzes your screen content in real-time and adjusts your monitor's gamma and contrast curves to maximize dynamic range. Think of it as auto-exposure for your monitor.

### **The Technology Stack**
- **Screen Capture:** PIL (Python Imaging Library) for screen grabs
- **Hardware Control:** Windows GDI32 API for direct gamma/contrast adjustment
- **Analysis Engine:** NumPy for fast mathematical processing
- **Input Handling:** Keyboard library for hotkey controls
- **Configuration:** JSON for persistent settings storage

### **The Analysis Pipeline**

#### **1. Screen Sampling**
```
Screen → 15 Sample Areas → RGB Values → Luma Calculation
```
- Captures 15 strategic regions across your screen
- Converts RGB to luma (perceived brightness) using standard formula
- Samples every 10ms for responsive feedback

#### **2. Scene Classification**
```
Luma Values → 23-Scene System → Scene Type (VERY_DARK, DARK, etc.)
```
Uses a sophisticated 23-point system:
- VERY_DARK (<0.00): Almost black content
- DARK (0.00-0.04): Very dark scenes  
- LOWER_DARK (0.04-0.08): Dark scenes
- MID_DARK (0.08-0.12): Moderately dark
- UPPER_DARK (0.12-0.16): Slightly dark
- ...continuing through 23 precise categories
- BRIGHT (>0.84): Very bright content

#### **3. Profile Application**
```
Scene Type + Profile → Gamma/Contrast/Brightness Values
```
Two optimized profiles:
- **Game Profile:** Aggressive shadow boosting for competitive gaming
- **Movie Profile:** Balanced luminance lift for cinematic viewing

#### **4. Hardware Adjustment**
```
Target Values → Windows GDI32 API → Monitor Gamma Ramp
```
- Directly modifies monitor's gamma lookup tables
- Changes are instantaneous and system-wide
- Affects all applications and games

### **The Intelligence Features**

#### **Safety Lock System**
- **Default:** Locked (prevents accidental changes)
- **Unlock:** Hold Ctrl+Alt to enable adjustments
- **Purpose:** Prevents interference while typing/working

#### **Smooth Transitions**
- **Smoothing Factor:** 0.1 (adjustable 0.05-0.9)
- **Purpose:** Natural-feeling adjustments without jarring
- **Implementation:** Gradual interpolation between current and target values

#### **Performance Optimization**
- **Frame Skipping:** Analyzes every 2nd frame (configurable)
- **Fast Mode:** Smaller sample regions for better performance
- **Result:** Minimal CPU impact (<1% on modern systems)

## 🛠️ Complete Setup Guide for Non-Programmers

### **Step 1: Install Python (The Foundation)**
1. Go to [python.org](https://www.python.org/downloads/)
2. Download Python 3.8 or newer (3.12 recommended)
3. **CRITICAL:** During installation, check "Add Python to PATH"
4. Verify installation: Open Command Prompt and type `python --version`

### **Step 2: Download ScreenBooster**
1. Download the ZIP file from GitHub
2. Extract to a folder (e.g., `C:\ScreenBooster`)
3. Navigate to that folder in File Explorer

### **Step 3: Install Dependencies (The Magic Libraries)**
**Method A: Easy Way (Recommended)**
1. Open Command Prompt in the ScreenBooster folder
   - Shift+Right-click in folder → "Open PowerShell window here"
2. Type: `pip install -r requirements.txt`
3. Wait for installation to complete

**Method B: Manual Way (If above fails)**
```bash
pip install numpy pillow keyboard
```

### **Step 4: Run ScreenBooster**
**Method A: Python Script (Developers/Advanced Users)**
```bash
python main.py
```

**Method B: Standalone EXE (Everyone Else)**
1. Download the pre-built EXE from GitHub Releases
2. Run `ScreenBoosterV4.exe`
3. No Python installation needed!

### **Step 5: First-Time Configuration**
1. Choose your profile (Game for gaming, Movie for movies)
2. Start ScreenBooster (Option 1)
3. Hold Ctrl+Alt to unlock adjustments
4. Use hotkeys to fine-tune:
   - G/Shift+G: Increase/Decrease Gamma
   - C/Shift+C: Increase/Decrease Contrast  
   - B/Shift+B: Increase/Decrease Brightness
5. Press S to save your settings

## 🎮 Using ScreenBooster - Daily Operation

### **Starting the Program**
1. Run `main.py` or the EXE
2. Select option 1 to start ScreenBooster
3. The program will begin analyzing and adjusting automatically

### **Understanding the Display**
```
UPPER_MID | γ1.00 C1.00 B0.95 | Custom: γ1.00 C1.00 B0.95 | Δγ-0.00 ΔC-0.00 ΔB-0.00 | Luma: 0.500
```
- **Scene Type:** Current scene classification
- **γ/C/B:** Current gamma, contrast, brightness values
- **Custom:** Target values for current scene
- **Δγ/ΔC/ΔB:** Difference from default (shows adjustment strength)
- **Luma:** Current screen brightness (0.0 = black, 1.0 = white)

### **Keyboard Controls**
**Safety First:** Hold Ctrl+Alt for all adjustments

**Adjustment Controls:**
- G: Increase Gamma (brighten dark areas)
- Shift+G: Decrease Gamma
- C: Increase Contrast (enhance detail)
- Shift+C: Decrease Contrast
- B: Increase Brightness (overall brightness)
- Shift+B: Decrease Brightness

**Profile Controls:**
- P: Switch to Game Profile
- Shift+P: Switch to Movie Profile

**Utility Controls:**
- R: Reset current scene to defaults
- S: Manually save settings
- Ctrl+C: Exit and restore defaults

### **Profile Differences**

#### **Game Profile** 🎮
- **Purpose:** Competitive gaming advantage
- **Characteristics:** Aggressive shadow boosting, high contrast
- **Best for:** FPS games, competitive play, dark environments
- **Typical Settings:** VERY_DARK γ5.0 C2.7 (extreme shadow boost)

#### **Movie Profile** 🎬  
- **Purpose:** Cinematic experience
- **Characteristics:** Balanced luminance, natural contrast
- **Best for:** Movies, streaming, general content
- **Typical Settings:** VERY_DARK γ5.4 C2.6 (strong but balanced)

## 🔧 Advanced Configuration

### **Accessing Configuration Menu**
1. Run main.py
2. Select option 2: Configuration Menu
3. Adjust parameters in real-time

### **Key Parameters Explained**

#### **Performance Settings**
- **Smoothing (0.05-0.9):** Transition speed
  - Lower = slower, smoother changes
  - Higher = faster, more responsive
  - Default: 0.1 (balanced)

- **Refresh Rate (0.001-0.1):** Analysis frequency
  - Lower = more responsive, higher CPU
  - Higher = less responsive, lower CPU
  - Default: 0.03 (33Hz analysis)

#### **Scene Thresholds**
- **Dark Threshold (0.01-0.99):** Where dark scenes begin
- **Bright Threshold (0.01-0.99):** Where bright scenes begin
- **23 total thresholds** for precise scene classification

### **Scene-Specific Tuning**
1. Access Scene Settings Menu (Option 3)
2. Select scene type (1-9)
3. Fine-tune gamma/contrast/brightness for each scene
4. Settings automatically saved

## 🚨 Troubleshooting Guide

### **Common Issues & Solutions**

#### **"ModuleNotFoundError: No module named 'X'"**
**Cause:** Missing Python libraries
**Solution:** Run `pip install -r requirements.txt`

#### **"Permission denied: screenbooster_profiles.json"**
**Cause:** EXE running from system directory
**Solution:** Use V4+ with fixed file paths, or run from local folder

#### **"input(): lost sys.stdin"**
**Cause:** EXE trying to show console menu
**Solution:** Use V4+ fixed EXE or run Python script directly

#### **"No changes visible on screen"**
**Cause:** Safety lock enabled
**Solution:** Hold Ctrl+Alt to unlock adjustments

#### **"Adjustments too aggressive"**
**Cause:** Profile settings too strong
**Solution:** 
1. Access Scene Settings Menu
2. Reduce gamma/contrast values
3. Save new profile

#### **"Performance issues"**
**Cause:** Analysis too frequent
**Solution:**
1. Increase Refresh Rate in Configuration Menu
2. Enable Fast Mode
3. Increase Skip Frames

### **Getting Help**
1. Check this troubleshooting section first
2. Review configuration files for corruption
3. Reset to defaults if needed
4. GitHub Issues for technical support

## 🎯 Advanced Usage Scenarios

### **Competitive Gaming Setup**
1. Use Game Profile
2. Set smoothing to 0.05 (fast response)
3. Enable safety lock during gameplay
4. Fine-tune dark scenes for visibility

### **Movie Watching Setup**  
1. Use Movie Profile
2. Set smoothing to 0.2 (smooth transitions)
3. Disable safety lock for automatic adjustment
4. Calibrate for your room lighting

### **Productivity Work**
1. Use Movie Profile (balanced)
2. Set higher smoothing (0.3+)
3. Keep safety lock enabled
4. Adjust mid-range scenes for comfort

## 🔬 Technical Architecture

### **File Structure**
```
ScreenBoosterV4/
├── main.py                    # Main application (640+ lines)
├── requirements.txt           # Python dependencies
├── screenbooster_profiles.json # User profile settings
├── screenbooster_config.json  # Configuration parameters
├── README.md                  # This documentation
├── CONFIGURATION.md           # Detailed config guide
├── BUILD_INSTRUCTIONS.md      # Build from source
└── ScreenBoosterV4.spec       # PyInstaller build script
```

### **Core Functions**
- `analyze_screen()`: Multi-region screen analysis
- `get_scene_type()`: 23-scene classification algorithm
- `apply_settings()`: Hardware gamma/contrast adjustment
- `smooth_transition()`: Natural interpolation system
- `save_profiles()`: Persistent settings storage

### **Data Flow**
```
Screen Capture → Luma Analysis → Scene Detection → Profile Lookup → Settings Application → Hardware Control
```

### **Performance Characteristics**
- **CPU Usage:** <1% on modern systems
- **Memory Usage:** ~50MB
- **Response Time:** <30ms
- **Analysis Rate:** 33Hz (adjustable)

## 🔮 Future Development

### **Potential Enhancements**
- HDR monitor support
- Per-application profiles
- GUI interface
- Automatic calibration
- Cloud profile sync
- Linux/macOS support

### **Contributing**
1. Fork the repository
2. Create feature branch
3. Submit pull request
4. Follow code style guidelines

## 📄 License & Disclaimer

**License:** MIT License - Free to use, modify, distribute

**Disclaimer:** 
- This software modifies monitor settings at hardware level
- Use at your own risk
- Not responsible for display damage or eye strain
- Consult monitor manufacturer guidelines
- Take breaks during extended use

## 🙏 Acknowledgments

**To the Community:** Thanks to everyone who provided feedback during the 4-version development cycle. Your reports of flickering, performance issues, and usability problems helped shape V4 into the polished solution it is today.

**Technical Credits:**
- PIL/Pillow for screen capture capabilities
- NumPy for high-performance mathematical operations
- Windows GDI32 API for direct hardware control
- PyInstaller for standalone EXE creation

---

**ScreenBooster V4 represents hundreds of hours of development, testing, and refinement.** What started as a simple gamma adjustment script evolved into a sophisticated auto-exposure system through trial, error, and community feedback. Version 4 achieves the perfect balance of power, usability, and performance that earlier versions could only dream of.

**Enjoy your enhanced viewing experience!** 🎬🎮
