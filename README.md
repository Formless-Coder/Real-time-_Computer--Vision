# Real-time Computer Vision on Mac

A Flask app that watches your face and hands. Recognizes expressions, lets you control system volume by pinching your fingers, and detects basic hand gestures. Runs on M-series Macs using MediaPipe and OpenCV.

---

## What It Does

### Expression Recognition
The app watches your face and tries to figure out what you're feeling. It looks at the positions of key points on your face – like your mouth corners, eyelids, and eyebrows – and makes a guess about whether you're happy, sad, angry, surprised, or just neutral. It's not perfect, especially in bad lighting, but it works surprisingly well once you figure out how close to sit to the camera.

- 😊 **Happy** – When you smile. It looks for an open mouth and corners that curve up.
- 😢 **Sad** – When your mouth is closed or the corners point down.
- 😠 **Angry** – When your eyebrows are close together and your expression gets tight.
- 😲 **Surprise** – When you open your mouth and eyes wide.
- 😐 **Neutral** – Everything else. The default state.

### Hand-Based Volume Control
Pinch your thumb and index finger together and the system volume drops. Open them up and it gets louder. Make a fist and the system mutes. The distance between your fingertips gets mapped to 0-100% volume. It's a bit touchy at first – the detection can be finicky if you move too fast or if the room is dark – but you'll get used to it.

### Basic Hand Gestures  
The app recognizes a few hand shapes:
- **OK sign** – Touch your thumb to your index finger to form a circle.
- **Wave** – Move your hand back and forth horizontally a few times. Useful for triggering actions.
- **Fist** – Close your hand. This triggers the mute function.

---

## Folder Layout

```
stellaris-hack/
├── app.py                    Main backend code
├── requirements.txt          What you need to install
├── start.sh                  Quick launch script
├── check_system.py           Checks if everything's set up right
├── README.md                 This file
├── TECHNICAL.md              Details about how it works
├── QUICKSTART.md             Quick reference
├── templates/
│   └── index.html           The web dashboard
└── static/                   Place for extra files if needed
```

## Getting Started

### What You Need
- A Mac with M1, M2, M3 chip (or newer). Older Intel Macs might work but they're not tested.
- Python 3.8 or higher. Check with `python3 --version`.
- A working webcam.
- About 5 minutes and a decent internet connection for the first install (downloading dependencies is the main wait).

### Installation

**Step 1:** Open Terminal and go to the project folder.
```bash
cd ~/Documents/stellaris-hack
```

**Step 2:** If you want to keep things clean, create a virtual environment. This keeps the app's dependencies separate from your system Python.
```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 3:** Install what the app needs.
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

The first time, this takes a couple minutes because it's downloading MediaPipe and OpenCV. Subsequent times are much faster.

**Step 4:** Give the app permission to use your camera.
- Go to System Preferences → Security & Privacy → Camera
- Find Terminal (or whatever you're using to run the app) and allow it

**Step 5:** Run it.
```bash
python app.py
```

You should see something like:
```
🎬 Starting Real-time Computer Vision System...
📍 Open browser to: http://localhost:5001
```

**Step 6:** Open your browser to `http://localhost:5001` and you're good. It'll ask for camera permission one more time in the browser itself – click allow.

---

## Using It

### Testing Expression Recognition
Sit in front of your webcam and try different expressions. The app updates every frame, so you should see it respond quickly. Fair warning: it works better with good lighting. If you're in a dark room, it'll struggle. Also, don't expect movie-level accuracy – it's pretty good but not perfect. Sometimes it confuses Surprise with a genuine smile.

### Controlling Volume
Make a **thumb‑index pinch** (tips touching) and then **slide your hand horizontally** across the camera view. Volume is mapped to the *x* coordinate of the pinch: left edge is 0 %, right edge is 100 %. Pinch and move left‑to‑right to raise the volume, right‑to‑left to lower it. A full fist still mutes the system.

A manual slider is available under the volume card if the gesture isn’t behaving. The pinch position must remain visible to the camera, and smooth, deliberate motion works best; very fast swipes or poor lighting will still produce jitter.
### Hand Gestures
- **OK Sign:** Touch your thumb to your index finger. Hold it steady for a second so the app registers it.
- **Wave:** Move your hand left and right a few times. The app looks for repeated direction changes, so make it obvious.
- **Fist:** Close your hand. All fingers should curl in. This triggers mute.

---

## The Dashboard

When you open the app in your browser, you'll see:

- **Video stream** – Your face and hands with overlays showing the landmarks the app is tracking.
- **Expression display** – Shows what the app thinks you're expressing right now.
- **Volume indicator** – Shows the current system volume (0-100) and a visual bar that fills up.
- **Status info** – Shows detected gesture and other real-time data.

The whole page is responsive, so it should work fine on your phone too if you want to view it remotely on the same network.

---

## How It Works (The Short Version)

MediaPipe gives us a bunch of points on your face (468 landmarks) and on your hands (21 per hand). The app calculates ratios and distances between these points:

- For expressions, it looks at mouth opening, eye opening, and the curve of your smile.
- For volume, it measures the distance between your thumb tip and index tip.
- For gestures, it checks if fingers are curled, if certain fingers are touching, or if your hand is moving in a pattern.

OpenCV handles the video capture and drawing the landmarks on the screen. Flask serves the video stream to your browser as MJPEG (basically a series of JPEG images sent one after another).

For volume control, the app uses `osascript` to send AppleScript commands to macOS. Direct system integration – it actually changes your Mac's volume.

---

## Troubleshooting

### Camera Isn't Working
First check: Is your webcam actually connected? Try FaceTime or Zoom to see if it works there.

If that works but this app doesn't:
1. Check System Preferences → Security & Privacy → Camera. Make sure Terminal (or your IDE) is in the allowed apps list.
2. Run the diagnostics: `python check_system.py`
3. If it still doesn't work, try restarting Terminal or your IDE.

### Volume Control Doesn't Work
Test osascript directly:
```bash
osascript -e "set volume output volume 50"
```

If you get an error, check System Preferences → Security & Privacy → Microphone. The app might need microphone permission to control audio.

If that works in Terminal but not in the app, it might be a permission issue with the Python process. Try running the app directly without any virtualenv stuff and see if that helps.

A manual slider has been added to the dashboard beneath the volume card – you can use it with your mouse to set the volume directly if the pinch gesture is unreliable.  It will always reflect whatever the current system volume is.

### Expression Detection Seems Wrong
This is common. A few things to try:
- **Better lighting** – The app works way better in well-lit rooms. Shadow on your face confuses it. The live feed will even display a red warning if the average brightness drops too low.
- **Low‑light enhancement** – A CLAHE (adaptive histogram equalization) step is applied when the feed is very dark. This improves contrast without turning the image monochrome; you should now see more color and detail even in dim conditions. It’s not a miracle cure, though – if the sensor only captures noise, software can’t invent color.
- **Higher JPEG quality** – The stream now uses 95 % quality to reduce compression artifacts and preserve color fidelity. This may slightly increase bandwidth/use on the local loop but makes the picture look much sharper.
- **Smoothed volume control** – Volume readings are filtered over a short history and only updated when the change exceeds a small threshold, preventing jitter when you move or wave your hand. Volume is also frozen while performing a wave gesture.
- **Pinch‑slide control** – Volume is determined by the horizontal position of a thumb‑index pinch. Keep the tips together and move your hand left/right to adjust the volume. This is more intuitive and avoids erratic readings from finger spacing.- **Gesture robustness/visibility** – wave detection no longer affects volume; a dedicated Gesture card appears on the dashboard (next to Expression & Volume). The in‑camera overlay also shows the gesture clearly.
- **Processing safety** – timeouts and exception handlers have been added around face/hand processing. If MediaPipe ever hangs or throws an error while you move your hands, the stream will continue using the last good frame instead of going black. Flaky camera reads are also retried.
- **Overlay text** – the in‑camera overlay now has a dark background and larger font so expression/gesture/volume values are legible. The web dashboard also increased font sizes.- **Camera access** – macOS may ask you to grant permission when the server first tries to open the camera. If the feed stays black, check **System Preferences → Security & Privacy → Camera** and make sure the terminal/Python process is allowed.
- **Exposure/brightness controls** – we attempt to tweak the webcam’s exposure/brightness properties when the stream starts, but not all cameras respect these settings. Try an external USB webcam if the built‑in one remains dark.
- **Browser support** – the video window uses an MJPEG stream; Safari sometimes only shows the first frame. If the image freezes after a moment, try Chrome or Firefox, or reload the page. The server adds cache‑control headers to mitigate this, but switching browsers is the most reliable fix.
- **Closer to camera** – Sit about 12-18 inches from the camera. Too far and the landmarks aren't detailed enough.
- **Different background** – If your background is all white or all black, try sitting somewhere with more contrast.
- **Relax** – Sometimes the app mistakes a neutral face for sadness if you're just sitting there tired. Exaggerate your expressions a bit.

### App is Slow or Stuttering
The app is pushing a lot of ML models through your Mac. A few things that help:

- Close other apps, especially browsers with lots of tabs.
- The video resolution is set to 800x600 by default. If your Mac is struggling, you can lower it even more in `app.py` around line 150.
- JPEG compression is set to quality 80. You can lower it to 70 if streaming is laggy.
- Face Mesh and Hand detection thresholds can be tweaked for speed vs. accuracy in `app.py` lines 25-35.

### Port 5000 Already in Use
Some other app is using port 5000. Edit the last line of `app.py` to use a different port:
```python
app.run(debug=True, port=8080)  # Use 8080 instead
```

---

## Customization

All the thresholds and parameters are adjustable. Here are the ones you'll probably want to tweak:

### Expression Thresholds
In `app.py`, the `detect_expression()` function has numbers like:
```python
if mouth_opening > 0.15:  # Lower this to 0.12 for easier happy detection
```

Lower the number to make detection easier, raise it to make it stricter.

### Volume Range
The pinch distance gets mapped to volume. Currently it goes from 0.02 (pinched) to 0.20 (open). You can adjust these:
```python
volume = (thumb_index_dist - 0.02) / 0.18 * 100
#        ↑ minimum distance    ↑ range
```

Smaller range = more sensitive. Larger range = more forgiving.

### Camera Settings
Around line 150 in `app.py`:
```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
```

Higher resolution = better quality, slower. Lower = faster, grainier.

### Disable Visual Overlay
If you don't want to see all the landmarks and lines on the video, comment out the drawing calls in `process_frame()`:
```python
# mp_drawing.draw_landmarks(frame, face_landmarks, ...)
```

---

## Performance

On an M2 Mac, expect:
- 25-30 actual frames per second (targets 30, usually achieves 25-28)
- About 15-20ms per frame for detection
- 250-300MB of RAM in use
- 25-35% CPU usage
- Noticeable delay? Probably around 50ms from real world to display

This isn't a problem for what the app does. It feels responsive even at 25 FPS.

---

## Under the Hood

The app runs with three main Python libraries:

**MediaPipe** – Does the heavy lifting. It uses pre-trained neural networks to find 468 points on your face and 21 points on each hand. Google's team trained these models and optimized them for actual phones and laptops, so they're pretty efficient. Apple Silicon specifically gets some optimizations.

**OpenCV** – A classic computer vision library. Handles reading from your webcam, drawing the landmarks on the frames, and encoding the video as JPEG.

**Flask** – A lightweight web framework. Serves the dashboard HTML page and streams the video to your browser.

The app captures frames from your camera, runs them through both MediaPipe models (face and hands), then calculates distances and ratios between the landmarks. For expressions, it's looking at about 5-6 key measurements. For gestures, it's checking finger positions and distances. These get converted to the expression name or gesture type, which then updates the web dashboard.

### Backend Architecture

#### MediaPipe Models
```python
# Face Mesh: 468 facial landmark points
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

# Hands: 21 landmark points per hand
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=0  # Lightweight for M2
)
```

#### Expression Detection Math
```python
def detect_expression(landmarks):
    mouth_opening = distance(upper_lip, lower_lip) / mouth_width
    eye_openness = distance(top_eyelid, bottom_eyelid)
    smile_curve = mouth_upper_y - avg(smile_corners_y)
    
    if mouth_opening > 0.15 and eye_openness > 0.012:
        return "Happy" if smile_curve < -0.01 else "Surprise"
    # ... more logic
```

#### Volume Control Math
```python
def pinch_center_to_volume(hand_landmarks):
    # assume thumb tip (4) and index tip (8) are touching
    thumb = hand_landmarks[4]
    index = hand_landmarks[8]
    center_x = (thumb.x + index.x) / 2.0  # normalized 0-1
    volume = int(max(0, min(100, center_x * 100)))
    set_system_volume(volume)  # osascript command
```

#### macOS Integration
```bash
# Set volume to 75%
osascript -e "set volume output volume 75"

# Mute system
osascript -e "set volume output muted true"

# Unmute system
osascript -e "set volume output muted false"
```

### Flask Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Render main dashboard (index.html) |
| `/video_feed` | GET | Stream MJPEG video (multipart/x-mixed-replace) |
| `/status` | GET | Return JSON: `{expression, volume}` |

### Video Stream Generator
Uses generator function for efficient multipart streaming:
```python
def video_feed_generator():
    while True:
        ret, frame = cap.read()
        processed = process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', processed)
        yield b'--frame\r\n' + b'Content-Type: image/jpeg\r\n' + ...
```

---

## 📊 Frontend Dashboard

### Components
- **Video Stream:** Centered img tag with MJPEG from `/video_feed`
- **Status Cards:** Expression & Volume with live updates
- **Info Grid:** Gesture descriptions and controls
- **Legend:** Expression states reference
- **Connection Status:** Real-time indicator

### Updates Mechanism
- AJAX requests to `/status` every 500ms
- Updates expression display and volume bar
- Fallback for disconnection handling

---

## 🎨 Customization

### Adjust Expression Thresholds
Edit `detect_expression()` in app.py:
```python
if mouth_opening > 0.15:  # Decrease for more sensitive happy detection
    return "Happy"
```

### Adjust Volume Sensitivity
The mapping now uses the **x‑coordinate of the thumb-index pinch center**.  You can tweak
`process_frame()` where `center_x` is calculated or adjust the `detect_pinch` threshold
for how close the fingers must be.
```python
# in process_frame, after gesture == "Pinch":
center_x, _ = get_thumb_index_center(hand_landmarks.landmark)
volume = int(max(0, min(100, center_x * 100)))
```
# optionally change the threshold in `detect_pinch` if you're having trouble
# getting the pinch detected early enough (default is 0.05).
### Change Camera Resolution
Edit `video_feed_generator()`:
```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)   # Increase for better quality
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
```

### Disable Face Mesh Visualization
Comment out in `process_frame()`:
```python
# mp_drawing.draw_landmarks(frame, face_landmarks, ...)
```

---

## 🐛 Troubleshooting

### Camera Not Working
```bash
# Check camera access
ls -la /dev/video*

# Grant permissions in System Preferences → Security & Privacy
# Add Terminal to Camera allowed apps
```

### Volume Control Not Working
```bash
# Test osascript directly
osascript -e "set volume output volume 50"
osascript -e "set volume output muted true"

# Verify permissions: Settings → Privacy & Security → Microphone
```

### Low FPS / Performance
1. Reduce camera resolution (see customization above)
2. Decrease detection confidence thresholds
3. Use `model_complexity=0` for hands (already done)
4. Close unnecessary browser tabs

### Hand Recognition Poor Quality
1. Ensure good lighting
   * If the video box appears very dark or almost black, the app will overlay a warning message in red text.
   * The stream is local (no network involved), so "poor connection" usually means the camera feed is low-quality or blocked.
   * Position yourself near a window or lamp and remove any obstructions from the webcam.
2. Increase `min_detection_confidence` (default 0.7)
3. Keep hands fully visible in frame

---

## 📈 Performance Metrics (M2 Mac)

| Metric | Value |
|--------|-------|
| Camera Resolution | 800x600 |
| Target FPS | 30 |
| Face Detection Latency | ~15ms |
| Hand Detection Latency | ~12ms |
| Memory Usage | ~250-300MB |
| CPU Usage | 25-35% |

---

## 🔐 Privacy & Safety

- No data is sent to external servers
- Video processing happens entirely on your machine
- Camera feed only used for local processing
- No recording or storage of frames

---

## 📚 Dependencies & Versions

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.3.2 | Web framework |
| OpenCV | 4.8.0.76 | Computer vision processing |
| MediaPipe | 0.10.0 | ML models for face/hand detection |
| NumPy | 1.24.3 | Numerical computations |
| Werkzeug | 2.3.6 | WSGI utilities |

---

## 🚀 Advanced Usage

### Adding New Gestures
1. Create a detection function in `app.py`:
```python
def detect_pinch(hand_landmarks):
    thumb_tip = hand_landmarks[4]
    middle_tip = hand_landmarks[12]
    distance = get_distance(thumb_tip, middle_tip)
    return distance < 0.05
```

2. Call in `process_frame()` and return gesture name

### Running on Different Port
```bash
# Replace port 5000 in last line of app.py:
app.run(debug=True, port=8080)
```

### Deploying to Remote Server
1. Use production WSGI server (Gunicorn):
```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

2. Update camera source to network stream or handle headless mode

---

## 📝 Notes & Limitations

- **Single Face:** Current setup supports 1 face per frame
- **Hand Count:** Supports up to 2 hands (can be increased)
- **Lighting:** Works best in well-lit environments
- **Background:** Works better with contrasting backgrounds
- **Occlusion:** Handles partial hand occlusion well

---

## 🎓 Learning Resources

- [MediaPipe Hands Documentation](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
- [MediaPipe Face Mesh](https://developers.google.com/mediapipe/solutions/vision/face_detector)
- [OpenCV Python Tutorials](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

## 📄 License

This project is provided as-is for educational and personal use.

---

## 🤝 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all dependencies are installed
3. Ensure camera permissions are granted
4. Check console output for specific error messages

---

**Built for macOS Silicon | Optimized for M2 & M3**

Last Updated: March 5, 2026
