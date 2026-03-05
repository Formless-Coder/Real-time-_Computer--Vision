# Quick Reference & Setup Guide
## Real-time Computer Vision System - Get Started in 5 Minutes

---

## 📂 Complete Project Structure

```
stellaris-hack/
│
├── 📄 app.py                    (550+ lines - Main Flask backend)
│   ├─ Face Mesh processing
│   ├─ Hand gesture recognition
│   ├─ Expression detection algorithm
│   ├─ Volume control system
│   ├─ Video streaming generator
│   └─ Flask routes (/video_feed, /status, /)
│
├── 📄 requirements.txt          (Python dependencies)
│   ├─ Flask 2.3.2
│   ├─ OpenCV 4.8.0.76
│   ├─ MediaPipe 0.10.0
│   └─ NumPy 1.24.3
│
├── 📄 start.sh                  (Automated startup script)
│   ├─ Creates venv
│   ├─ Installs dependencies
│   └─ Launches Flask app
│
├── 📄 check_system.py           (Diagnostics tool)
│   ├─ Verifies Python 3.8+ 
│   ├─ Checks all dependencies
│   ├─ Tests camera access
│   ├─ Tests volume control
│   └─ Checks directory structure
│
├── 📄 README.md                 (Complete documentation)
│   ├─ Features & capabilities
│   ├─ Installation steps
│   ├─ Usage guide
│   ├─ Troubleshooting
│   └─ Performance metrics
│
├── 📄 TECHNICAL.md             (Advanced documentation)
│   ├─ Landmark indices & maps
│   ├─ Mathematical formulas
│   ├─ Algorithm breakdowns
│   ├─ Configuration parameters
│   └─ Performance details
│
├── 📁 templates/
│   └── 📄 index.html            (Web interface frontend)
│       ├─ Video stream display
│       ├─ Status dashboard
│       ├─ Real-time updates
│       └─ Responsive design
│
└── 📁 static/                   (CSS/JS assets - optional)
    └── (Currently empty - can add custom assets here)
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Navigate to project
```bash
cd ~/Documents/stellaris-hack
```

### Step 2: Run setup script
```bash
bash start.sh
```
(Takes 2-3 minutes first time for dependency installation)

### Step 3: Open browser
```
http://localhost:5001   # default port changed to 5001 to avoid conflicts
```

---

## 🔍 Verify Setup Before Running

```bash
python check_system.py
```

This will check:
- ✅ Python version
- ✅ All required packages
- ✅ Camera access
- ✅ macOS osascript availability
- ✅ Volume control capability
- ✅ Project file structure

---

## 🎮 Using the Application

### Expression Detection
| Expression | How to Trigger |
|-----------|-----------------|
| **Happy** 😊 | Smile with open mouth |
| **Sad** 😢 | Close mouth and lower face |
| **Angry** 😠 | Furrow eyebrows, tight mouth |
| **Surprise** 😲 | Open mouth and eyes wide |
| **Neutral** 😐 | Relax face |

### Volume Control
| Gesture | Action |
| **Open** | No action |
| **Fist** | Mute system |
| **OK** | (reserved) |
| **Wave** | Toggle special feature |
|---------|--------|
| **Pinch** 👌 | Thumb & index tips touching, slide hand left/right to adjust volume |
| **Fist** ✊ | All fingers curled = Mute |

> **Tip:** A manual volume slider appears beneath the volume status card in the dashboard. Use it if hand gestures aren’t responding.
### Hand Gestures
| Gesture | How to Trigger |
|---------|-----------------|
| **OK** ⭕ | Touch thumb to index (circle) |
| **Wave** 👋 | Move hand left-right repeatedly |

---

## 📊 Dashboard Display

### Video Stream
- Live MJPEG feed (30 FPS)
- Real-time landmark visualization
- Face mesh & hand skeletons overlay

### Status Cards
- **Current Expression:** Updated in real-time
- **System Volume:** Shows 0-100%, visual bar indicator

### Info Grid
- Hand gesture descriptions
- Volume is controlled by pinching your thumb and index finger and sliding horizontally
- Wave detection explanation
- Legend of all expression states

---

## 🛠️ Manual Startup (Alternative to start.sh)

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

---

## 🐛 Troubleshooting Quick Fixes

### Camera Not Working
```bash
# Grant permissions: System Preferences → Security → Privacy → Camera
# Add Terminal/IDE to allowed apps

# Or run system check:
python check_system.py
```

### Volume Control Not Working
```bash
# Test osascript directly:
osascript -e "set volume output volume 50"

# Check permissions: System Preferences → Privacy & Security → Microphone
```

### Low FPS (Frame Rate)
1. Close other apps
2. Reduce camera resolution in app.py (line ~150)
3. Reduce confidence thresholds

### Expression Not Detecting Correctly
1. Improve lighting
   * The video window will show a 'Low light' warning if it can't see you clearly.
   * "Poor connection" messages usually mean the camera feed is dark or blocked, not a network issue.
2. Get closer to camera
3. Increase expression thresholds in app.py (lines ~90-100)

### Stream Freezes When Hands Appear
- If the video goes black or hangs while using hand gestures, the app now caches the last working frame and continues streaming. Keep the server running and refresh the page if a freeze occurs. Check the `/status` endpoint for error logs and timestamps.

### Port 5000 Already in Use
```bash
# Edit last line of app.py:
# app.run(debug=True, port=8080)  # Use 8080 instead
```

---

## 📝 Key Code Locations

| Feature | File | Lines |
|---------|------|-------|
| **Expression Detection** | app.py | 80-120 |
| **Volume Mapping** | app.py | 185-200 |
| **Hand Gestures** | app.py | 140-180 |
| **Landmark Math** | app.py | 45-75 |
| **Video Generator** | app.py | 280-330 |
| **Flask Routes** | app.py | 340-420 |
| **Frontend Design** | templates/index.html | 30-120 |
| **Status Updates** | templates/index.html | 230-250 |

---

## 💡 Tips & Tricks

### Improve Expression Detection
1. Good lighting is essential – if the box stays black, check macOS camera permissions and make sure the terminal has access.
2. Face should be 12-24 inches from camera
3. Background should be contrasting (not all white/black)

### Improve Volume Control
1. Hand should be fully visible
2. Keep fingers spread slightly
3. Move hand smoothly
4. Practice the pinch-and-slide motion: keep thumb & index together, then move hand left/right

### Improve Gesture Recognition
1. Wear contrasting clothing
2. Keep hands in view
3. Make gestures clearly and deliberately
4. Wave with consistent speed

### Performance Tuning
| Parameter | Location | Effect |
|-----------|----------|--------|
| Camera Resolution | app.py:150 | Higher = better quality, lower FPS |
| JPEG Quality | app.py:325 | Lower = faster streaming |
| Detection Confidence | app.py:25-35 | Lower = more lenient |
| Thresholds | app.py:90-100 | Adjust for sensitivity |

---

## 🔧 Customization Examples

### Change Port
```python
# Last line of app.py:
app.run(debug=True, port=8080)  # Instead of 5000
```

### Disable Face Mesh Visualization
```python
# In process_frame(), comment line ~280:
# mp_drawing.draw_landmarks(frame, face_landmarks, ...)
```

### Adjust Volume Range
```python
# adjust mapping or threshold used when the pinch is detected:
def detect_pinch(hand_landmarks, thresh=0.05):
    thumb = hand_landmarks[4]
    index = hand_landmarks[8]
    return get_distance(thumb, index) < thresh

# and in process_frame:
# center_x = (thumb.x + index.x) / 2.0
# volume = int(max(0, min(100, center_x * 100)))
```

### Change Expression Thresholds
```python
# In detect_expression():
if mouth_opening > 0.20:  # Make happier detection easier
    return "Happy"
```

---

## 📈 Performance Expectations

| Metric | M2 Mac |
|--------|--------|
| Actual FPS | 25-30 |
| Face Detection Latency | ~15ms |
| Hand Detection Latency | ~12ms |
| Expression Update Interval | ~100ms |
| Total CPU Usage | 25-35% |
| Memory Usage | ~250-300MB |

---

## 🌐 Accessing from Mobile Device

For local network testing:

1. Find your Mac IP:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. Edit app.py last line:
   ```python
   app.run(host='0.0.0.0', port=5000)
   ```

3. On mobile, visit:
   ```
   http://YOUR_MAC_IP:5000
   ```

⚠️ **Note:** Camera stream requires 2+ Mbps bandwidth

---

## 📞 Support Resources

- **ReadMe:** Full features & setup guide
- **Technical:** Advanced algorithms & math
- **System Check:** Diagnose issues
- **Code Comments:** Inline documentation in app.py

---

## ✅ Checklist Before First Run

- [ ] Python 3.8+ installed
- [ ] In stellaris-hack directory
- [ ] Camera connected & working
- [ ] macOS (M1/M2/M3+)
- [ ] Camera permissions granted
- [ ] Run `python check_system.py` ✅
- [ ] Browser ready

---

## 🎬 Example Session

```bash
# 1. Navigate
cd ~/Documents/stellaris-hack

# 2. Check system (optional but recommended)
python check_system.py

# 3. Start application
bash start.sh

# 4. Watch output:
# 🎬 Starting Real-time Computer Vision System...
# 📍 Open browser to: http://localhost:5001

# 5. Open browser to http://localhost:5001

# 6. Allow camera access when prompted

# 7. Express different emotions, control volume with hand gestures!

# 8. Stop with Ctrl+C
```

---

**Ready to go!** 🎉

If you encounter issues, run `python check_system.py` first, then consult README.md troubleshooting section.

For advanced customization, see TECHNICAL.md for algorithm details and configuration parameters.
