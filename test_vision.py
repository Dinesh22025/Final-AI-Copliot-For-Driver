import cv2
import base64
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.vision import DriverMonitor

print("=" * 60)
print("TESTING DRIVER MONITOR VISION SYSTEM")
print("=" * 60)

# Initialize monitor
print("\n1. Initializing DriverMonitor...")
try:
    monitor = DriverMonitor()
    print("✓ DriverMonitor initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    sys.exit(1)

# Capture from webcam
print("\n2. Capturing frame from webcam...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("✗ Cannot open webcam")
    sys.exit(1)

ret, frame = cap.read()
cap.release()

if not ret:
    print("✗ Failed to capture frame")
    sys.exit(1)

print(f"✓ Frame captured: {frame.shape}")

# Convert to base64
print("\n3. Converting frame to base64...")
_, buffer = cv2.imencode('.jpg', frame)
frame_b64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
print(f"✓ Base64 length: {len(frame_b64)}")

# Analyze
print("\n4. Analyzing frame...")
result = monitor.analyze(frame_b64)

print("\n" + "=" * 60)
print("ANALYSIS RESULTS:")
print("=" * 60)
print(f"Status:      {result['status']}")
print(f"Confidence:  {result['confidence'] * 100:.1f}%")
print(f"Faces:       {result['faces']}")
print(f"EAR:         {result['ear']}")
print(f"MAR:         {result['mar']}")
print(f"Head Tilt:   {result['head_tilt']}°")
print(f"Gaze Offset: {result['gaze_offset']}%")
print("=" * 60)

if result['faces'] > 0:
    print("\n✓ SUCCESS: Face detection is working!")
else:
    print("\n✗ WARNING: No faces detected")
    print("  - Make sure you're in front of the camera")
    print("  - Check lighting conditions")
    print("  - Try moving closer to the camera")

print("\nTest complete!")
