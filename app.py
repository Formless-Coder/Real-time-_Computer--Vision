#!/usr/bin/env python3
"""
Real-time Computer Vision Project
Expression Detection | Volume Control | Sign Recognition
Running on Flask with MediaPipe and OpenCV
"""

import os
import cv2
import math
import subprocess
import mediapipe as mp
from flask import Flask, render_template, Response, request
from collections import deque
import numpy as np

# ============================================================================
# INITIALIZATION
# ============================================================================

app = Flask(__name__)

# MediaPipe setup (optimized for Apple Silicon)
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    model_complexity=0
)

# Global state tracking
current_expression = "Neutral"
current_gesture = "Open"
current_volume = 50
last_frame = None
gesture_buffer = deque(maxlen=10)  # Track hand positions for gesture recognition
wave_threshold = 0.05  # Threshold for detecting wave motion


# ============================================================================
# HELPER FUNCTIONS: LANDMARK MATH & GEOMETRY
# ============================================================================

def get_distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


def get_angle(point1, point2, point3):
    """Calculate angle between three points (in degrees)."""
    a = get_distance(point1, point2)
    b = get_distance(point2, point3)
    c = get_distance(point1, point3)
    
    if a == 0 or b == 0:
        return 0
    
    cos_angle = (a**2 + b**2 - c**2) / (2 * a * b)
    cos_angle = max(-1, min(1, cos_angle))  # Clamp to [-1, 1]
    return math.degrees(math.acos(cos_angle))


def get_mouth_openness(landmarks):
    """Calculate mouth openness ratio (0-1 scale). Higher = more open."""
    # Landmarks: 13(upper lip), 14(lower lip inner), 17(lower lip), 0(nose)
    upper_lip = landmarks[13]  # Upper lip center
    lower_lip = landmarks[14]  # Lower lip inner
    mouth_width_left = landmarks[61]
    mouth_width_right = landmarks[291]
    
    mouth_opening = get_distance(upper_lip, lower_lip)
    mouth_width = get_distance(mouth_width_left, mouth_width_right)
    
    if mouth_width == 0:
        return 0
    return mouth_opening / mouth_width


def get_eye_openness(landmarks, is_right=False):
    """Calculate eye openness ratio (0-1 scale). Higher = more open."""
    if is_right:
        # Right eye landmarks: 386(top), 374(bottom), 380(inner), 362(outer)
        top = landmarks[386]
        bottom = landmarks[374]
    else:
        # Left eye landmarks: 159(top), 145(bottom), 133(inner), 33(outer)
        top = landmarks[159]
        bottom = landmarks[145]
    
    return get_distance(top, bottom)


def get_eyebrow_distance(landmarks, is_right=False):
    """Calculate distance between eyebrows (indicator of anger)."""
    if is_right:
        eyebrow = landmarks[46]  # Right eyebrow center
        inner_eye = landmarks[133]
    else:
        eyebrow = landmarks[276]  # Left eyebrow center
        inner_eye = landmarks[362]
    
    return get_distance(eyebrow, inner_eye)


def detect_expression(landmarks):
    """Detect facial expression using landmark ratios."""
    mouth_opening = get_mouth_openness(landmarks)
    left_eye = get_eye_openness(landmarks, is_right=False)
    right_eye = get_eye_openness(landmarks, is_right=True)
    avg_eye_openness = (left_eye + right_eye) / 2
    
    # eyebrow spacing (furrowed brows indicate anger)
    brow_left = get_eyebrow_distance(landmarks, is_right=False)
    brow_right = get_eyebrow_distance(landmarks, is_right=True)
    avg_brow = (brow_left + brow_right) / 2
    
    # Smile detection: estimate upward/downward curve of mouth
    smile_left_y = landmarks[84].y
    smile_right_y = landmarks[314].y
    mouth_upper_y = landmarks[13].y
    smile_curve = mouth_upper_y - (smile_left_y + smile_right_y) / 2
    
    # prioritized classification
    # angry: furrowed brows or downward curved mouth
    if avg_brow < 0.03 or smile_curve > 0.015:
        return "Angry"
    # surprise: wide open mouth or very open eyes
    if mouth_opening > 0.18 or avg_eye_openness > 0.02:
        return "Surprise"
    # happy: upward curve or slight smile with open mouth
    if smile_curve < -0.012 or mouth_opening > 0.14 and smile_curve < -0.005:
        return "Happy"
    # sad: closed mouth and eyes
    if mouth_opening < 0.06 and avg_eye_openness < 0.008:
        return "Sad"
    return "Neutral"


# ============================================================================
# HAND GESTURE RECOGNITION
# ============================================================================

def detect_fist(hand_landmarks):
    """Detect if hand is in a fist gesture."""
    # Fist: all fingers curled, fingertips below knuckles
    # Use thumb tip, index tip, middle tip, ring tip, pinky tip
    finger_tips = [4, 8, 12, 16, 20]
    finger_pips = [3, 6, 10, 14, 18]  # Proximal interphalangeal joints
    
    curled_count = 0
    for tip, pip in zip(finger_tips, finger_pips):
        if hand_landmarks[tip].y > hand_landmarks[pip].y:
            curled_count += 1
    
    return curled_count >= 4


def detect_ok_sign(hand_landmarks):
    """Detect OK sign (thumb and index touching in a circle)."""
    thumb_tip = hand_landmarks[4]
    index_tip = hand_landmarks[8]
    middle_tip = hand_landmarks[12]
    
    # OK sign: thumb and index close together, other fingers up
    thumb_index_dist = get_distance(thumb_tip, index_tip)
    
    # Middle finger should be further away (pointing up)
    middle_dist = get_distance(index_tip, middle_tip)
    
    is_ok = thumb_index_dist < 0.05 and middle_dist > 0.08
    return is_ok


def detect_wave(hand_positions):
    """Detect wave gesture by tracking horizontal hand motion."""
    if len(hand_positions) < 5:
        return False
    
    # Calculate horizontal displacement over recent frames
    recent_x = [pos[0] for pos in hand_positions]
    
    # Check for oscillating left-right motion
    displacement = abs(recent_x[-1] - recent_x[0])
    
    # Wave: significant horizontal movement with multiple direction changes
    if displacement > wave_threshold:
        direction_changes = 0
        for i in range(1, len(recent_x) - 1):
            if (recent_x[i] - recent_x[i-1]) * (recent_x[i+1] - recent_x[i]) < 0:
                direction_changes += 1
        
        return direction_changes >= 2
    
    return False


def detect_pinch(hand_landmarks, thresh=0.05):
    """Return True if thumb and index tips are touching (pinch)."""
    thumb = hand_landmarks[4]
    index = hand_landmarks[8]
    return get_distance(thumb, index) < thresh


def detect_hand_gesture(hand_landmarks):
    """Classify hand gestures. Return 'Open' if none matched."""
    if detect_fist(hand_landmarks):
        return "Fist"
    if detect_ok_sign(hand_landmarks):
        return "OK"
    if detect_pinch(hand_landmarks):
        return "Pinch"
    # other gestures could be added here
    return "Open"


def get_index_middle_distance(hand_landmarks):
    """Get normalized distance between index tip (8) and middle tip (12).

    This function is retained for backwards compatibility but is no
    longer used for volume control.
    """
    index_tip = hand_landmarks[8]
    middle_tip = hand_landmarks[12]
    return get_distance(index_tip, middle_tip)


def get_thumb_index_center(hand_landmarks):
    """Return (x,y) midpoint between thumb tip (4) and index tip (8)."""
    thumb = hand_landmarks[4]
    index = hand_landmarks[8]
    return ((thumb.x + index.x) / 2.0, (thumb.y + index.y) / 2.0)


# ============================================================================
# macOS SYSTEM INTEGRATION
# ============================================================================

def set_system_volume(volume_level):
    """Set macOS system volume using osascript.

    Includes logging for debugging and ensures value is clamped.
    """
    volume_level = max(0, min(100, int(volume_level)))
    print(f"[set_system_volume] setting volume to {volume_level}")
    try:
        subprocess.run(
            ['osascript', '-e', f'set volume output volume {volume_level}'],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to set volume: {e}")


def set_system_mute(mute=True):
    """Mute/unmute macOS system using osascript."""
    try:
        state = "true" if mute else "false"
        subprocess.run(
            ['osascript', '-e', f'set volume output muted {state}'],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to set mute: {e}")


# ============================================================================
# MAIN PROCESSING FUNCTION
# ============================================================================

def process_frame(frame):
    """Process a single frame: detect face, hands, expressions, gestures."""
    global current_expression, current_volume, current_gesture
    
    h, w, c = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Initialize results
    expression = "Neutral"
    gesture = "Open"
    volume = current_volume
    is_muted = False
    
    # ---- FACE MESH PROCESSING ----
    try:
        face_results = face_mesh.process(frame_rgb)
    except Exception as e:
        print(f"[process_frame] face_mesh error: {e}")
        face_results = None
    
    if face_results and face_results.multi_face_landmarks:
        try:
            landmarks = face_results.multi_face_landmarks[0].landmark
            expression = detect_expression(landmarks)
            current_expression = expression
        except Exception as e:
            print(f"[process_frame] expression error: {e}")
        
        # Draw face mesh (optional - light rendering)
        for face_landmarks in face_results.multi_face_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                face_landmarks,
                mp_face_mesh.FACEMESH_TESSELATION,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=0),
                mp_drawing.DrawingSpec(color=(100, 100, 100), thickness=1)
            )
    
    # ---- HAND PROCESSING ----
    try:
        hand_results = hands.process(frame_rgb)
    except Exception as e:
        print(f"[process_frame] hands.process error: {e}")
        hand_results = None
    
    if hand_results and hand_results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):
            # Gesture detection
            gesture = detect_hand_gesture(hand_landmarks.landmark)
            current_gesture = gesture
            
            # Volume control: thumb-index pinch sliding horizontally
            if gesture == "Wave":
                volume = current_volume
            elif gesture == "Pinch":
                # compute horizontal position of the pinch center
                center_x, _ = get_thumb_index_center(hand_landmarks.landmark)
                # map normalized x (0.0 left, 1.0 right) to 0-100
                raw_vol = int(max(0, min(100, center_x * 100)))
                process_frame.volume_history.append(raw_vol)
                avg_vol = sum(process_frame.volume_history) / len(process_frame.volume_history)
                if abs(avg_vol - current_volume) > 2:
                    current_volume = int(avg_vol)
                volume = current_volume
            else:
                # no relevant gesture: keep last volume
                volume = current_volume
            
            # Fist = mute
            if gesture == "Fist":
                is_muted = True
                set_system_mute(True)
            else:
                is_muted = False
                set_system_mute(False)
                try:
                    set_system_volume(volume)
                except Exception:
                    pass
            
            # Track hand position for wave detection
            hand_center_x = hand_landmarks.landmark[9].x  # Wrist center
            gesture_buffer.append((hand_center_x, hand_landmarks.landmark))
            
            # Wave detection
            if detect_wave([(pos[0], pos[1]) for pos in gesture_buffer]):
                gesture = "Wave"
            
            # Draw hand landmarks
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(200, 0, 0), thickness=2)
            )
    
    return frame, expression, gesture, volume, is_muted


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')


@app.route('/set_volume', methods=['POST'])
def set_volume():
    """Endpoint used by the frontend slider to set volume manually."""
    global current_volume
    data = None
    try:
        data = request.get_json()
    except Exception as e:
        print(f"[set_volume] invalid json: {e}")
        return ({'error': 'invalid json'}, 400)

    if not data or 'volume' not in data:
        return ({'error': 'missing volume'}, 400)

    try:
        vol = int(data['volume'])
    except ValueError:
        return ({'error': 'bad volume value'}, 400)

    current_volume = max(0, min(100, vol))
    set_system_mute(False)
    set_system_volume(current_volume)
    return ({'success': True, 'volume': current_volume}, 200)


def video_feed_generator():
    """Generator function for video feed stream."""
    global current_expression, current_volume, last_frame
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[video_feed] warning: camera could not be opened")
    
    # Optimize camera settings for M2
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    # try to open exposure/brightness controls (may not work on all devices)
    try:
        cap.set(cv2.CAP_PROP_EXPOSURE, -4)   # lower number = longer exposure on some cams
        cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)
    except Exception:
        pass
    
    def _frame_brightness(img):
        # convert to grayscale and return mean intensity
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return float(np.mean(gray))

    def _enhance_low_light(img):
        # if very dark, apply CLAHE (adaptive histogram equalization) on Y channel
        gray_val = _frame_brightness(img)
        if gray_val < 60:
            yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            yuv[:, :, 0] = clahe.apply(yuv[:, :, 0])
            img = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        return img

    frame_count = 0
    try:
        while True:
            try:
                ret, frame = cap.read()
            except Exception as e:
                print(f"[video_feed] exception during read: {e}")
                ret = False
                frame = None
            
            if not ret or frame is None:
                # if we have a last good frame, keep sending it instead of breaking
                if last_frame is not None:
                    yield last_frame
                    continue
                else:
                    print("[video_feed] cap.read() returned False, no fallback frame")
                    break
            
            frame_count += 1
            if frame_count % 30 == 0:
                print(f"[video_feed] frame#{frame_count}")
            
            frame = cv2.flip(frame, 1)
            frame = _enhance_low_light(frame)
            # safe call to processing to prevent freezes
            start_proc = cv2.getTickCount()
            try:
                processed_frame, expression, gesture, volume, is_muted = process_frame(frame)
            except Exception as e:
                print(f"[video_feed] process_frame exception: {e}")
                processed_frame = frame.copy()
                expression = current_expression
                gesture = current_gesture
                volume = current_volume
                is_muted = False
            end_proc = cv2.getTickCount()
            proc_time = (end_proc - start_proc) / cv2.getTickFrequency()
            
            # check ambient brightness and warn if too dark
            br = _frame_brightness(processed_frame)
            if br < 50:  # threshold empirically chosen
                cv2.putText(processed_frame,
                            "⚠ Low light - improve lighting",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 0, 255),
                            2)
            
            # Add text overlay with a background for visibility
            status_text = f"Expression: {expression} | Gesture: {gesture}"
            volume_text = f"Volume: {volume}" + (" (Muted)" if is_muted else "")
            cv2.rectangle(processed_frame, (10, 10), (550, 120), (0, 0, 0), -1)
            cv2.putText(
                processed_frame,
                status_text,
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3
            )
            cv2.putText(
                processed_frame,
                volume_text,
                (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3
            )
            
            # Encode frame to JPEG (higher quality for better clarity)
            ret, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            frame_bytes = buffer.tobytes()
            
            # Yield frame for streaming
            # if processing is very slow, hold previous frame instead
            if 'proc_time' in locals() and proc_time > 0.25 and last_frame is not None:
                yield last_frame
            else:
                frame_chunk = (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n'
                       + frame_bytes + b'\r\n')
                last_frame = frame_chunk
                yield frame_chunk
    
    finally:
        cap.release()


@app.route('/video_feed')
def video_feed():
    """Stream video feed with multipart/x-mixed-replace."""
    # add headers to disable caching; some browsers (Safari) capture only first frame
    # direct_passthrough allows Flask to send bytes without buffering
    return Response(
        video_feed_generator(),
        mimetype='multipart/x-mixed-replace; boundary=frame',
        headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Connection': 'keep-alive'
        },
        direct_passthrough=True
    )


@app.route('/status')
def status():
    """Return current status as JSON for dashboard updates."""
    from flask import jsonify
    return jsonify({
        'expression': current_expression,
        'gesture': current_gesture,
        'volume': current_volume
    })


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("🎬 Starting Real-time Computer Vision System...")
    print("📍 Open browser to: http://localhost:5001")
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5001)
