# Technical Documentation - MediaPipe Landmarks & Algorithms
## Real-time Computer Vision System

---

## 📍 MediaPipe Face Mesh Landmarks

### Overview
Face Mesh provides **468 3D facial landmarks** that map key facial features. These landmarks are used to calculate ratios and distances for expression detection.

### Key Landmark Indices

#### Upper Face (Eyes & Eyebrows)
| Function | Left | Right | Description |
|----------|------|-------|-------------|
| Top Eyelid | 159 | 386 | Upper edge of eye |
| Bottom Eyelid | 145 | 374 | Lower edge of eye |
| Inner Corner | 133 | 362 | Close to nose |
| Outer Corner | 33 | 263 | Side of face |
| Eyebrow Inner | 107 | 336 | Inner eyebrow point |
| Eyebrow Center | 276 | 46 | Middle of eyebrow |
| Eyebrow Outer | 66 | 296 | Outer eyebrow point |

#### Mouth & Lips
| Function | Index | Description |
|----------|-------|-------------|
| Upper Lip Center | 13 | Center top lip |
| Lower Lip Inner | 14 | Inside lower lip |
| Lip Left Corner | 61 | Left mouth corner |
| Lip Right Corner | 291 | Right mouth corner |
| Upper Lip Left | 84 | Left upper lip |
| Upper Lip Right | 314 | Right upper lip |

#### Nose
| Function | Index | Description |
|----------|-------|-------------|
| Nose Tip | 1 | Tip of nose |
| Nose Left | 98 | Left nostril |
| Nose Right | 327 | Right nostril |

#### Face Geometry
| Function | Index | Description |
|----------|-------|-------------|
| Chin | 152 | Bottom of chin |
| Forehead | 10 | Between eyebrows |

---

## 🤚 MediaPipe Hands Landmarks

### Overview
Each hand has **21 3D landmarks** organized by finger and joint type.

### Landmark Structure

```
        4 (Thumb Tip)
        |
        3 (Thumb IP)
        |
        2 (Thumb MCP)
        |
        1 (Thumb CMC)
    
    8 (Index Tip)      12 (Middle Tip)     16 (Ring Tip)      20 (Pinky Tip)
    |                  |                   |                  |
    7 (Index PIP)      11 (Middle PIP)     15 (Ring PIP)      19 (Pinky PIP)
    |                  |                   |                  |
    6 (Index MCP)      10 (Middle MCP)     14 (Ring MCP)      18 (Pinky MCP)
    |                  |                   |                  |
    -------- 5 (Hand Center / Palm) --------
            |
            0 (Wrist)
```

### Landmark Indices

| Finger | Tip | PIP | MCP | CMC |
|--------|-----|-----|-----|-----|
| Thumb | 4 | 3 | 2 | 1 |
| Index | 8 | 7 | 6 | 5 |
| Middle | 12 | 11 | 10 | 9 |
| Ring | 16 | 15 | 14 | 13 |
| Pinky | 20 | 19 | 18 | 17 |
| Wrist | 0 | — | — | — |
| Palm | 5-9 | — | — | — |

**Abbreviations:**
- TIP: Finger tip (furthest point)
- PIP: Proximal Interphalangeal joint
- MCP: Metacarpophalangeal joint
- CMC: Carpometacarpal joint (only thumb)

---

## 📐 Mathematical Formulas

### 1. Euclidean Distance
**Formula:** 
$$d = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$$

**Usage in project:**
- Volume control: distance between thumb tip and index tip
- Gesture detection: distance between fingers for OK sign
- Expression: distance between eyelids for eye openness

```python
def get_distance(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
```

### 2. Angle Between Three Points
**Formula (Law of Cosines):**
$$\cos(\theta) = \frac{a^2 + b^2 - c^2}{2ab}$$
$$\theta = \arccos\left(\frac{a^2 + b^2 - c^2}{2ab}\right)$$

Where:
- $a$ = distance(point1, point2)
- $b$ = distance(point2, point3)  
- $c$ = distance(point1, point3)

**Usage in project:**
- Detecting eyebrow angles for anger
- Analyzing mouth curve for smile detection

```python
def get_angle(point1, point2, point3):
    a = get_distance(point1, point2)
    b = get_distance(point2, point3)
    c = get_distance(point1, point3)
    cos_angle = (a**2 + b**2 - c**2) / (2 * a * b)
    cos_angle = max(-1, min(1, cos_angle))
    return math.degrees(math.acos(cos_angle))
```

### 3. Normalized Ratio (0-1 Scale)
**Formula:**
$$\text{ratio} = \frac{\text{measured distance}}{\text{reference distance}}$$

**Usage in project:**
- Mouth openness: `distance(upper_lip, lower_lip) / mouth_width`
- Eye openness: `distance(top_eyelid, bottom_eyelid) / eye_width`

```python
def get_mouth_openness(landmarks):
    mouth_opening = get_distance(upper_lip, lower_lip)
    mouth_width = get_distance(mouth_left, mouth_right)
    return mouth_opening / mouth_width if mouth_width > 0 else 0
```

### 4. Linear Interpolation (Volume Mapping)
**Formula:**
$$\text{output} = \text{min} + \frac{\text{input} - \text{in}_\text{min}}{\text{in}_\text{max} - \text{in}_\text{min}} \times (\text{max} - \text{min})$$

**Usage in project:**
- Volume is driven by the **x‑coordinate of the thumb–index pinch center** (0.0 at left edge of camera frame, 1.0 at right edge). The value is simply scaled to 0–100.

```python
def pinch_x_to_volume(x_coord):
    # x_coord in [0.0, 1.0]
    return int(max(0, min(100, x_coord * 100)))
```

(earlier versions mapped the thumb-index distance; that logic remains in code for reference but is no longer used.)

---

## 😊 Expression Detection Algorithm

### Decision Tree

```
START: Analyze facial landmarks
│
├─ Calculate: mouth_opening, eye_openness, smile_curve
│
├─ IF mouth_opening > 0.15 AND eye_openness > 0.012
│  │
│  ├─ IF smile_curve < -0.01 (mouth corners up)
│  │  └─ RETURN "Happy" ✓
│  │
│  └─ ELSE
│     └─ RETURN "Surprise" ✓
│
├─ IF smile_curve < -0.015 AND mouth_opening < 0.12
│  └─ RETURN "Happy" ✓
│
├─ IF mouth_opening < 0.08 AND eye_openness < 0.010
│  └─ RETURN "Sad" ✓
│
├─ IF smile_curve > 0.02 AND mouth_opening < 0.10
│  └─ RETURN "Angry" ✓
│
└─ DEFAULT
   └─ RETURN "Neutral" ✓
```

### Thresholds (Configurable)

```python
# Mouth
MOUTH_OPEN_THRESHOLD = 0.15      # Anything above = attempting smile/laugh
MOUTH_CLOSED_THRESHOLD = 0.08    # Closed mouth
SMILE_CURVE_THRESHOLD = -0.015   # Upward mouth curve

# Eyes
EYE_OPEN_THRESHOLD = 0.012       # Eyes noticeably open
EYE_SURPRISE_THRESHOLD = 0.015   # Very wide eyes

# Emotional markers
HAPPY_SMILE_CURVE = -0.01        # Corners curved up
ANGRY_CURVE = 0.02               # Corners curved down
```

### Smile Curve Calculation

```python
def calculate_smile_curve(landmarks):
    mouth_upper = landmarks[13].y      # Upper lip center
    smile_left = landmarks[84].y       # Left mouth corner
    smile_right = landmarks[314].y     # Right mouth corner
    
    # If result is NEGATIVE: corners are UP (smile)
    # If result is POSITIVE: corners are DOWN (frown)
    smile_curve = mouth_upper - (smile_left + smile_right) / 2
    return smile_curve
```

---

## 👋 Gesture Recognition

### 1. Wave Detection

**Algorithm:**
1. Track hand wrist position over 10 frames
2. Calculate horizontal (x-axis) displacement
3. Count direction changes
4. If displacement > threshold AND direction_changes ≥ 2 → WAVE

**Code:**
```python
def detect_wave(hand_positions):
    recent_x = [pos[0] for pos in hand_positions[-5:]]
    displacement = abs(recent_x[-1] - recent_x[0])
    
    direction_changes = 0
    for i in range(1, len(recent_x) - 1):
        # Check if direction changed (product < 0)
        if (recent_x[i] - recent_x[i-1]) * (recent_x[i+1] - recent_x[i]) < 0:
            direction_changes += 1
    
    return displacement > 0.05 and direction_changes >= 2
```

### 2. OK Sign Detection

**Criteria:**
- Thumb tip and index tip very close (distance < 0.05)
- Other fingers extended away (distance > 0.08)
- Forms a circle shape

**Code:**
```python
def detect_ok_sign(hand_landmarks):
    thumb_tip = hand_landmarks[4]
    index_tip = hand_landmarks[8]
    middle_tip = hand_landmarks[12]
    
    thumb_index_dist = get_distance(thumb_tip, index_tip)
    middle_dist = get_distance(index_tip, middle_tip)
    
    return thumb_index_dist < 0.05 and middle_dist > 0.08
```

### 3. Fist Detection

**Criteria:**
- All 5 fingers curled
- Fingertips located BELOW their knuckles (PIP joints)

**Code:**
```python
def detect_fist(hand_landmarks):
    finger_tips = [4, 8, 12, 16, 20]      # Tip indices
    finger_pips = [3, 6, 10, 14, 18]      # PIP indices
    
    curled_count = 0
    for tip, pip in zip(finger_tips, finger_pips):
        # If tip Y > PIP Y, finger is curled
        if hand_landmarks[tip].y > hand_landmarks[pip].y:
            curled_count += 1
    
    return curled_count >= 4  # 4+ fingers curled = fist
```

---

## 🔊 Volume Control System

### Volume Mapping

**Raw Input:**
- Horizontal *x* coordinate of the thumb‑index pinch center, normalized 0–1 (0 = left edge of camera frame, 1 = right edge)

**Mapping Formula:**
$$\text{Volume\%} = 100 \times x_{pinch}$$

**Clamping:**
$$\text{Volume\%} = \max(0, \min(100, \text{Volume\%}))$$

(This replaces the earlier distance‑based mapping; the old formula is retained in the code comments for historical context.)
**Example:**
- Distance 0.02 → Volume 0%
- Distance 0.11 → Volume 50%
- Distance 0.20 → Volume 100%

### macOS System Integration

**AppleScript Commands:**

```bash
# Get current volume
osascript -e "get volume output volume"

# Set volume to X (0-100)
osascript -e "set volume output volume 75"

# Get mute status
osascript -e "get volume output muted"

# Set mute (true/false)
osascript -e "set volume output muted true"
osascript -e "set volume output muted false"
```

**Python subprocess call:**
```python
def set_system_volume(volume_level):
    volume_level = max(0, min(100, int(volume_level)))
    try:
        subprocess.run(
            ['osascript', '-e', f'set volume output volume {volume_level}'],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Volume control failed: {e}")
```

---

## 🎬 Video Processing Pipeline

### Frame Processing Flow

```
Raw Frame (800x600, BGR)
    ↓
1. Convert BGR → RGB
    ↓
2. Face Detection (Face Mesh)
    ├─ If face found:
    │  ├─ Extract landmarks
    │  ├─ Calculate expression
    │  ├─ Draw mesh on frame
    │  └─ Update global state
    └─ Otherwise: Skip face processing
    ↓
3. Hand Detection (Hands model)
    ├─ For each hand (max 2):
    │  ├─ Extract landmarks
    │  ├─ Detect gestures
    │  ├─ Calculate volume
    │  ├─ Control system volume
    │  ├─ Track for wave detection
    │  └─ Draw hand skeleton
    └─ Otherwise: Skip hand processing
    ↓
4. Add Text Overlays
    ├─ Status line (expression + gesture)
    └─ Volume indicator
    ↓
5. Encode to JPEG (quality 80)
    ↓
6. Stream via MJPEG format
```

### Performance Considerations

**M2 Mac Optimization:**
- Camera: 800x600 @ 30 FPS (not 4K)
- Face Mesh: `refine_landmarks=True` (better quality, slight latency)
- Hands: `model_complexity=0` (lightweight model)
- JPEG Quality: 80/100 (good quality, small file size)

**Typical Latencies:**
- Face Detection: 15-20ms
- Hand Detection: 10-15ms
- Expression Calculation: ~5ms
- Total per frame: ~40-50ms (20-25 FPS actual)

---

## 🌐 Frontend-Backend Communication

### Request Flow

```
┌─────────────────────────────────────────────┐
│         Frontend (index.html)               │
│  ┌─────────────────────────────────────┐   │
│  │ Display live MJPEG video stream     │   │
│  │ from /video_feed                    │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │ AJAX: fetch /status every 500ms     │   │
│  └─────────────────────────────────────┘   │
│          ↓                                  │
└──────────┼──────────────────────────────────┘
           │
    Backend (Flask app.py)
           │
    ┌──────┴──────────────┐
    │                     │
    ▼                     ▼
/video_feed          /status
├─ OpenCV capture    ├─ Return JSON
├─ MediaPipe detect  │  {
├─ Process frame     │    "expression": "Happy",
├─ Encode JPEG       │    "volume": 75
├─ Stream MJPEG      │  }
└─ Multipart/mixed   └─ 200 OK
```

### JSON Status Response
```json
{
  "expression": "Happy",
  "volume": 75,
  "gesture": "Open",
  "timestamp": 1709645234
}
```

---

## 🔧 Configuration Parameters

### Detection Confidence
```python
face_mesh = mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5,    # 0-1: raise for strict
    min_tracking_confidence=0.5      # 0-1: raise for stability
)

hands = mp_hands.Hands(
    min_detection_confidence=0.7,    # 0-1: raise for strict
    min_tracking_confidence=0.5      # 0-1: raise for stability
)
```

### Expression Thresholds (Adjustable)
```python
# Increase values for LESS sensitive detection
MOUTH_OPEN_THRESHOLD = 0.15         # For happy/surprise
EYE_OPEN_THRESHOLD = 0.012          # For surprise
SMILE_CURVE_THRESHOLD = -0.015      # For happy
```

### Volume Calibration
```python
# Adjust for different hand sizes
MIN_PINCH_DISTANCE = 0.02           # When pinched fully
MAX_PINCH_DISTANCE = 0.20           # When fully extended
```

---

## 📊 Frame Rate & Performance

### Optimal Settings for M2
- **Camera Resolution:** 800x600 (not 1280x720 or higher)
- **Target FPS:** 30 (mediaPipe can handle this)
- **Face Detection:** Every frame
- **Hand Detection:** Every frame
- **JPEG Compression:** Quality 80 (good balance)

### Memory Profile
| Component | Memory |
|-----------|--------|
| Face Mesh Model | ~50MB |
| Hands Model | ~30MB |
| OpenCV | ~20MB |
| Flask + Python | ~30MB |
| Frame Buffer | ~5MB |
| **Total** | **~135MB** |

---

## 🎓 Learning Resources

- [MediaPipe Documentation](https://developers.google.com/mediapipe)
- [Face Mesh Landmark Map](https://github.com/google/mediapipe/blob/master/mediapipe/solutions/face_mesh_connections.py)
- [Hand Landmark Map](https://github.com/google/mediapipe/blob/master/mediapipe/solutions/hands.py)
- [OpenCV Python Docs](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)

---

**Last Updated:** March 5, 2026  
**Platform:** macOS (M1/M2/M3+)  
**Version:** 1.0
