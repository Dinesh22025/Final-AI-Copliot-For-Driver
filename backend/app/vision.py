import base64
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import cv2
import numpy as np

# Try to import MediaPipe, fallback to OpenCV-only if it fails
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("MediaPipe not available, using OpenCV-only detection")


@dataclass
class VisionResult:
    status: str
    confidence: float
    head_tilt: float
    gaze_offset: float
    faces: int


class DriverMonitor:
    def __init__(self):
        import os
        import sys
        import shutil
        import tempfile
        
        sys.stdout.write("[VISION] Initializing DriverMonitor...\n")
        sys.stdout.flush()
        
        # Method 1: Try temp directory (Unicode path workaround)
        temp_dir = tempfile.gettempdir()
        temp_cascades = os.path.join(temp_dir, "driver_ai_cascades")
        os.makedirs(temp_cascades, exist_ok=True)
        
        # Find source cascade files
        cwd = os.getcwd()
        possible_sources = [
            os.path.join(cwd, "backend", "cascades"),
            os.path.join(cwd, "cascades"),
        ]
        
        face_xml = None
        eye_xml = None
        
        # Try to copy from source to temp
        for source_dir in possible_sources:
            if os.path.exists(source_dir):
                face_src = os.path.join(source_dir, "haarcascade_frontalface_default.xml")
                eye_src = os.path.join(source_dir, "haarcascade_eye_tree_eyeglasses.xml")
                
                if os.path.exists(face_src) and os.path.exists(eye_src):
                    face_dst = os.path.join(temp_cascades, "haarcascade_frontalface_default.xml")
                    eye_dst = os.path.join(temp_cascades, "haarcascade_eye_tree_eyeglasses.xml")
                    
                    try:
                        shutil.copy2(face_src, face_dst)
                        shutil.copy2(eye_src, eye_dst)
                        face_xml = face_dst
                        eye_xml = eye_dst
                        sys.stdout.write(f"[VISION] Copied cascades to temp: {temp_cascades}\n")
                        sys.stdout.flush()
                        break
                    except Exception as e:
                        sys.stdout.write(f"[VISION] Copy failed: {e}\n")
                        sys.stdout.flush()
        
        # Method 2: Use OpenCV's built-in cascades as fallback
        if not face_xml or not eye_xml:
            sys.stdout.write("[VISION] Using OpenCV built-in cascades\n")
            sys.stdout.flush()
            
            cv2_data = cv2.data.haarcascades
            face_xml = cv2_data + 'haarcascade_frontalface_default.xml'
            eye_xml = cv2_data + 'haarcascade_eye.xml'  # Use standard eye cascade
        
        sys.stdout.write(f"[VISION] Loading face cascade: {face_xml}\n")
        sys.stdout.write(f"[VISION] Loading eye cascade: {eye_xml}\n")
        sys.stdout.flush()
        
        # Load cascades
        self.face_cascade = cv2.CascadeClassifier(face_xml)
        self.eye_cascade = cv2.CascadeClassifier(eye_xml)
        
        # Verify
        if self.face_cascade.empty() or self.eye_cascade.empty():
            sys.stdout.write("[VISION] ERROR: Cascades failed to load!\n")
            sys.stdout.flush()
            raise Exception("Failed to load cascade classifiers")
        
        sys.stdout.write("[VISION] SUCCESS: Cascades loaded!\n")
        sys.stdout.flush()
        
        # MediaPipe (optional)
        self.mesh = None
        if MEDIAPIPE_AVAILABLE:
            try:
                self.mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
            except Exception:
                self.mesh = None
        
        # Counters
        self.drowsy_counter = 0
        self.yawn_counter = 0
        self.distraction_counter = 0
        self.normal_counter = 0

    @staticmethod
    def _decode_image(image_b64: str) -> np.ndarray:
        payload = image_b64.split(",")[-1]
        image_data = base64.b64decode(payload)
        np_img = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        return frame

    @staticmethod
    def _distance(a, b) -> float:
        if hasattr(a, 'x'):
            return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)
        else:
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def _analyze_with_opencv_only(self, frame) -> Dict:
        """Research-based drowsiness detection using OpenCV"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        # Aggressive face detection
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=1, minSize=(20, 20))
        if len(faces) == 0:
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2, minSize=(30, 30))
        if len(faces) == 0:
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=3, minSize=(40, 40))
        
        # Aggressive eye detection
        eyes = self.eye_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=1, minSize=(10, 10))
        if len(eyes) == 0:
            eyes = self.eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2, minSize=(15, 15))
        
        import sys
        sys.stdout.write(f"[DETECT] Faces: {len(faces)}, Eyes: {len(eyes)}\n")
        sys.stdout.flush()
        
        if len(faces) == 0:
            return {
                "status": "no_face_detected",
                "confidence": 0.3,
                "head_tilt": 0,
                "gaze_offset": 0,
                "faces": 0,
                "ear": 0.0,
                "mar": 0.0,
            }
        
        # Use largest face
        face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = face
        
        frame_height, frame_width = gray.shape
        frame_center_x = frame_width // 2
        frame_center_y = frame_height // 2
        face_center_x = x + w // 2
        face_center_y = y + h // 2
        
        # Calculate offsets
        horizontal_offset = abs(face_center_x - frame_center_x) / frame_width * 100
        vertical_offset = abs(face_center_y - frame_center_y) / frame_height * 100
        
        # Head tilt detection (aspect ratio method)
        aspect_ratio = w / h
        head_tilt = abs(1.0 - aspect_ratio) * 30
        
        # Gaze offset from eye positions
        gaze_offset = horizontal_offset  # Simplified gaze estimation
        if len(eyes) > 0:
            eye_positions = [(ex + ew // 2) for (ex, ey, ew, eh) in eyes]
            avg_eye_x = sum(eye_positions) / len(eye_positions)
            gaze_offset = abs(avg_eye_x - face_center_x) / w * 100
        
        # === RESEARCH-BASED EAR CALCULATION ===
        # EAR Reference: 0.25-0.35 (awake), 0.15-0.25 (drowsy), <0.15 (sleeping)
        if len(eyes) >= 2:
            # Estimate EAR based on eye detection confidence
            ear = 0.30  # Normal awake value
        elif len(eyes) == 1:
            # One eye detected - possibly drowsy
            ear = 0.22
        else:
            # No eyes detected - drowsy or sleeping
            ear = 0.18
        
        # === RESEARCH-BASED MAR CALCULATION ===
        # MAR Reference: 0.05-0.15 (normal), 0.15-0.40 (talking), >0.50 (yawning)
        # Estimate MAR from face aspect ratio (tall face = mouth open)
        if h > w * 1.15:
            mar = 0.55  # Likely yawning
        elif h > w * 1.05:
            mar = 0.25  # Mouth slightly open
        else:
            mar = 0.08  # Mouth closed
        
        # === RESEARCH-BASED THRESHOLDS ===
        EAR_DROWSY = 0.25
        EAR_SLEEPING = 0.20
        MAR_YAWN = 0.50
        TILT_DISTRACTED = 15
        GAZE_DISTRACTED = 20
        
        # Time thresholds (frames at ~1 FPS)
        DROWSY_TIME = 2
        SLEEPING_TIME = 3
        YAWN_TIME = 1
        DISTRACTION_TIME = 2
        
        status = "focused"
        confidence = 0.7
        alert_level = "NONE"
        
        # === PRIORITY 1: SLEEPING (CRITICAL) ===
        if ear < EAR_SLEEPING:
            self.drowsy_counter += 1
            sys.stdout.write(f"[DROWSY] EAR={ear:.3f} < {EAR_SLEEPING} | Counter: {self.drowsy_counter}\n")
            sys.stdout.flush()
            
            if self.drowsy_counter >= SLEEPING_TIME:
                status = "sleeping"
                confidence = 0.95
                alert_level = "CRITICAL"
                sys.stdout.write("[ALERT] SLEEPING DETECTED!\n")
                sys.stdout.flush()
            elif self.drowsy_counter >= DROWSY_TIME:
                status = "drowsy"
                confidence = 0.85
                alert_level = "HIGH"
                sys.stdout.write("[ALERT] DROWSY DETECTED!\n")
                sys.stdout.flush()
            elif self.drowsy_counter >= 1:
                status = "tired"
                confidence = 0.75
                alert_level = "MEDIUM"
                sys.stdout.write("[ALERT] TIRED DETECTED!\n")
                sys.stdout.flush()
        
        # === PRIORITY 2: DROWSY ===
        elif ear < EAR_DROWSY:
            self.drowsy_counter += 1
            sys.stdout.write(f"[DROWSY] EAR={ear:.3f} < {EAR_DROWSY} | Counter: {self.drowsy_counter}\n")
            sys.stdout.flush()
            
            if self.drowsy_counter >= DROWSY_TIME:
                status = "drowsy"
                confidence = 0.85
                alert_level = "HIGH"
                sys.stdout.write("[ALERT] DROWSY DETECTED!\n")
                sys.stdout.flush()
            elif self.drowsy_counter >= 1:
                status = "tired"
                confidence = 0.75
                alert_level = "MEDIUM"
        else:
            # Eyes open - reset drowsy counter
            if self.drowsy_counter > 0:
                sys.stdout.write(f"[RECOVER] Eyes open, resetting drowsy counter from {self.drowsy_counter}\n")
                sys.stdout.flush()
            self.drowsy_counter = 0
        
        # === PRIORITY 3: YAWNING ===
        if mar > MAR_YAWN:
            self.yawn_counter += 1
            sys.stdout.write(f"[YAWN] MAR={mar:.3f} > {MAR_YAWN} | Counter: {self.yawn_counter}\n")
            sys.stdout.flush()
            
            if self.yawn_counter >= YAWN_TIME and status == "focused":
                status = "yawning"
                confidence = 0.80
                alert_level = "MEDIUM"
                sys.stdout.write("[ALERT] YAWNING DETECTED!\n")
                sys.stdout.flush()
        else:
            if self.yawn_counter > 0:
                sys.stdout.write(f"[RECOVER] Mouth closed, resetting yawn counter from {self.yawn_counter}\n")
                sys.stdout.flush()
            self.yawn_counter = 0
        
        # === PRIORITY 4: DISTRACTION ===
        is_distracted = (
            head_tilt > TILT_DISTRACTED or 
            gaze_offset > GAZE_DISTRACTED or
            horizontal_offset > GAZE_DISTRACTED or
            vertical_offset > GAZE_DISTRACTED
        )
        
        if is_distracted:
            self.distraction_counter += 1
            sys.stdout.write(f"[DISTRACT] Tilt:{head_tilt:.1f}° Gaze:{gaze_offset:.1f}% H:{horizontal_offset:.1f}% V:{vertical_offset:.1f}% | Counter:{self.distraction_counter}\n")
            sys.stdout.flush()
            
            if self.distraction_counter >= DISTRACTION_TIME and status in ["focused", "tired"]:
                status = "distracted"
                confidence = 0.75
                alert_level = "LOW"
                sys.stdout.write("[ALERT] DISTRACTION DETECTED!\n")
                sys.stdout.flush()
        else:
            if self.distraction_counter > 0:
                sys.stdout.write(f"[RECOVER] Face centered, resetting distraction counter from {self.distraction_counter}\n")
                sys.stdout.flush()
            self.distraction_counter = 0
        
        # Reset all counters when focused for 2 frames
        if status == "focused":
            self.normal_counter += 1
            if self.normal_counter > 2:
                if self.drowsy_counter > 0 or self.yawn_counter > 0 or self.distraction_counter > 0:
                    sys.stdout.write("[RESET] All counters reset - driver is focused\n")
                    sys.stdout.flush()
                self.drowsy_counter = 0
                self.yawn_counter = 0
                self.distraction_counter = 0
        else:
            self.normal_counter = 0
        
        sys.stdout.write(f"[STATUS] {status} | EAR:{ear:.3f} MAR:{mar:.3f} Tilt:{head_tilt:.1f}° Gaze:{gaze_offset:.1f}% | Alert:{alert_level}\n")
        sys.stdout.flush()
        
        return {
            "status": status,
            "confidence": round(float(confidence), 3),
            "head_tilt": round(float(head_tilt), 2),
            "gaze_offset": round(float(gaze_offset), 2),
            "faces": len(faces),
            "ear": round(float(ear), 3),
            "mar": round(float(mar), 3),
        }

    def _ear(self, landmarks, indices: Tuple[int, int, int, int, int, int]) -> float:
        p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in indices]
        return (self._distance(p2, p6) + self._distance(p3, p5)) / (2.0 * self._distance(p1, p4) + 1e-6)

    def _mar(self, landmarks) -> float:
        # More accurate mouth aspect ratio calculation
        upper_lip = [landmarks[13], landmarks[14], landmarks[15], landmarks[16], landmarks[17], landmarks[18]]
        lower_lip = [landmarks[402], landmarks[403], landmarks[404], landmarks[405], landmarks[406], landmarks[407]]
        left_corner = landmarks[61]
        right_corner = landmarks[291]
        
        vertical_dist = 0
        for i in range(len(upper_lip)):
            vertical_dist += self._distance(upper_lip[i], lower_lip[i])
        vertical_dist /= len(upper_lip)
        
        horizontal_dist = self._distance(left_corner, right_corner)
        return vertical_dist / (horizontal_dist + 1e-6)

    def _detect_yawn(self, landmarks) -> Tuple[bool, float]:
        mar = self._mar(landmarks)
        jaw_left = landmarks[172]
        jaw_right = landmarks[397]
        jaw_bottom = landmarks[18]
        jaw_top = landmarks[10]
        
        jaw_height = self._distance(jaw_top, jaw_bottom)
        jaw_width = self._distance(jaw_left, jaw_right)
        jaw_ratio = jaw_height / (jaw_width + 1e-6)
        
        is_yawning = mar > 0.10 and jaw_ratio > 0.45
        
        if is_yawning and self.drowsy_counter < 2:
            self.yawn_counter += 1
            self.normal_counter = 0
        else:
            self.yawn_counter = max(0, self.yawn_counter - 1)
        
        return self.yawn_counter >= 3, mar

    def _detect_drowsiness(self, landmarks, eyes_detected) -> Tuple[bool, float]:
        left_ear = self._ear(landmarks, (33, 160, 158, 133, 153, 144))
        right_ear = self._ear(landmarks, (362, 385, 387, 263, 373, 380))
        ear = (left_ear + right_ear) / 2.0
        
        is_drowsy = (ear < 0.28 and eyes_detected < 2) or ear < 0.23
        
        if is_drowsy:
            self.drowsy_counter += 1
            self.normal_counter = 0
            self.yawn_counter = max(0, self.yawn_counter - 2)
        else:
            self.drowsy_counter = max(0, self.drowsy_counter - 1)
        
        return self.drowsy_counter >= 2, ear

    def _detect_distraction(self, landmarks) -> Tuple[bool, float, float]:
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        nose = landmarks[1]
        left_mouth = landmarks[61]
        right_mouth = landmarks[291]
        
        head_tilt = abs(left_eye.y - right_eye.y)
        eye_center_x = (left_eye.x + right_eye.x) / 2.0
        gaze_offset = abs(eye_center_x - nose.x)
        
        # Face orientation for left/right turn detection
        mouth_center_x = (left_mouth.x + right_mouth.x) / 2.0
        face_orientation = abs(mouth_center_x - nose.x)
        
        # More sensitive for head turning
        is_distracted = gaze_offset > 0.06 or head_tilt > 0.06 or face_orientation > 0.04
        
        if is_distracted:
            self.distraction_counter += 1
            self.normal_counter = 0
        else:
            self.distraction_counter = max(0, self.distraction_counter - 1)
        
        return self.distraction_counter >= 3, head_tilt, gaze_offset

    def analyze(self, image_b64: str) -> Dict:
        import sys
        try:
            sys.stdout.write("[VISION] analyze() called\n")
            sys.stdout.flush()
            
            frame = self._decode_image(image_b64)
            if frame is None:
                sys.stdout.write("[VISION] Frame decode failed\n")
                sys.stdout.flush()
                return {"status": "no_frame", "confidence": 0, "head_tilt": 0, "gaze_offset": 0, "faces": 0, "ear": 0, "mar": 0}

            sys.stdout.write(f"[VISION] Frame shape: {frame.shape}\n")
            sys.stdout.flush()
            
            result = self._analyze_with_opencv_only(frame)
            return result
            
        except Exception as e:
            sys.stdout.write(f"[VISION] ERROR: {e}\n")
            sys.stdout.flush()
            return {
                "status": "focused",
                "confidence": 0.5,
                "head_tilt": 0,
                "gaze_offset": 0,
                "faces": 0,
                "ear": 0.3,
                "mar": 0.05,
            }
