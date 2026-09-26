# ScreenBooster Configuration Guide

## How to Edit Behavior

### 1. Transition Speed (Most Important for Fast Response)
```python
SMOOTHING = 0.35  # Line 52
```
- **0.05**: Very smooth, slow transitions (good for movies)
- **0.15**: Moderate speed (balanced)
- **0.35**: Fast transitions (current setting)
- **0.8**: Very fast, almost instant (may feel jarring)

### 2. Scene Detection Sensitivity
```python
AGGRESSIVE_BOOST_THRESHOLD = 0.25  # Line 64 - Below this = DARK scene
BRIGHT_SCENE_THRESHOLD = 0.70     # Line 65 - Above this = BRIGHT scene
```
- **More sensitive**: 0.20/0.75 (triggers dark mode earlier)
- **Less sensitive**: 0.30/0.65 (requires darker/brighter scenes)

### 3. Contrast Intensity
```python
EXAGGERATED_CONTRAST_RANGE = 1.4  # Line 69 - Max contrast for dark scenes
SUBTLE_CONTRAST_RANGE = 1.15      # Line 70 - Contrast for bright scenes
```
- **Subtle**: 1.2/1.1 (minimal changes)
- **Balanced**: 1.4/1.15 (current)
- **Aggressive**: 1.6/1.25 (strong contrast)

### 4. Response Speed vs Stability
```python
CONTENT_HISTORY_SIZE = 15  # Line 74 - Frames to analyze
```
- **5**: Very fast response (less stable)
- **15**: Balanced (current)
- **30**: Very stable (slower response)

### 5. Performance vs Accuracy
```python
SAMPLE_SIZE = 120  # Line 60 - Screen area to analyze
```
- **80**: Faster processing (less accurate)
- **120**: Balanced (current)
- **200**: More accurate (slower)

## Quick Presets

### For Gaming (Fast Response)
```python
SMOOTHING = 0.6
CONTENT_HISTORY_SIZE = 5
SAMPLE_SIZE = 80
```

### For Movies (Smooth Transitions)
```python
SMOOTHING = 0.1
CONTENT_HISTORY_SIZE = 20
SAMPLE_SIZE = 150
```

### For Productivity (Balanced)
```python
SMOOTHING = 0.35
CONTENT_HISTORY_SIZE = 15
SAMPLE_SIZE = 120
```

## How to Apply Changes

1. Stop the program (Ctrl+C)
2. Edit the values in `main.py`
3. Restart the program
4. The new settings will be displayed on startup

## Advanced Settings

Only change these if you understand the technical details:

- `SHADOW_BOOST_THRESHOLD = 0.15` (Line 83)
- `HIGHLIGHT_BOOST_THRESHOLD = 0.85` (Line 84)
- `SHADOW_BOOST_MULTIPLIER = 2.0` (Line 85)
- `HIGHLIGHT_BOOST_MULTIPLIER = 0.5` (Line 86)
