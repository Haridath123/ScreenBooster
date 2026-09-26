# ScreenBooster - Auto-Exposure & Dynamic Range Optimizer

A Python program that dynamically adjusts screen gamma and contrast to maximize your LCD monitor's dynamic range with intelligent auto-exposure compensation.

## Features

- **Auto-Exposure System**: Intelligently boosts dark scenes and optimizes bright scenes
- **Dynamic Range Maximization**: Ensures darkest blacks are visible and brightest whites use full LCD capability
- **Scene Detection**: Automatically detects dark, mid, and bright scenes for optimal adjustment
- **Aggressive Dark Scene Boost**: Makes very dark content visible without losing detail
- **Natural Bright Scene Enhancement**: Subtle contrast enhancement for already bright content
- **Smooth Transitions**: Natural-feeling adjustments without jarring changes
- **Real-time Monitoring**: Live status display of current settings and scene type

## How It Works

The program analyzes screen content from multiple regions and applies intelligent exposure adjustments:

- **Very Dark Scenes** (<25% brightness): Aggressive exposure boost with enhanced contrast to make dark areas visible
- **Mid-Low to Mid Scenes** (25-70% brightness): Moderate exposure boost to optimize LCD dynamic range
- **Bright Scenes** (>70% brightness): Natural look with subtle contrast enhancement

## Key Algorithms

### Auto-Exposure Logic
- **Dark scenes**: Lower gamma (0.6-0.8) + high contrast (1.2-1.4) for aggressive brightening
- **Mid scenes**: Balanced gamma (0.75-1.0) + enhanced contrast (1.2-1.5) for optimal pop
- **Bright scenes**: Near-natural gamma (0.95-1.1) + subtle contrast (1.15-1.3)

### Dynamic Range Processing
- **Shadow boost**: Aggressive brightening for darkest areas (<15% luminance)
- **Highlight optimization**: Pushes bright areas (>85% luminance) to full LCD brightness
- **Percentile analysis**: Uses 1st and 99th percentiles for accurate dynamic range detection

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the program:
```bash
python main.py
```

The program will display real-time information:
- Scene type (DARK/MID/BRIGHT)
- Current gamma and contrast values
- Average luminance and dynamic range

Press `Ctrl+C` to stop and restore default settings.

## Configuration

Key parameters in `main.py`:

- `SMOOTHING`: Transition speed (0.05-1.0, default 0.12)
- `REFRESH_RATE`: Check frequency in seconds (default 0.016 for ~60fps)
- `AGGRESSIVE_BOOST_THRESHOLD`: Dark scene threshold (default 0.25)
- `BRIGHT_SCENE_THRESHOLD`: Bright scene threshold (default 0.70)
- `EXAGGERATED_CONTRAST_RANGE`: Maximum contrast for dark scenes (default 1.4)

## Technical Details

- Uses Windows GDI32 API for gamma ramp adjustment
- Samples 5 screen regions for comprehensive analysis
- Maintains 20-frame history for stable scene detection
- Percentile-based analysis for accurate dynamic range measurement
- Safe value clamping prevents extreme adjustments

## Safety

- Automatically restores default settings on exit
- Error handling prevents system instability
- Value clamping ensures safe adjustment ranges
- Smooth transitions prevent jarring changes

## Compatibility

- Windows only (uses Windows-specific APIs)
- Works with all LCD display types
- No administrator privileges required
- Optimized for both gaming and productivity content
