import os
import cv2

print("Testing cascade file loading...")
print(f"Current working directory: {os.getcwd()}")

# Try method 1: From CWD
cascades_dir = os.path.join(os.getcwd(), "backend", "cascades")
print(f"\nMethod 1 - CWD based:")
print(f"  Cascades dir: {cascades_dir}")
print(f"  Exists: {os.path.exists(cascades_dir)}")

if os.path.exists(cascades_dir):
    face_xml = os.path.join(cascades_dir, "haarcascade_frontalface_default.xml")
    eye_xml = os.path.join(cascades_dir, "haarcascade_eye_tree_eyeglasses.xml")
    print(f"  Face XML exists: {os.path.exists(face_xml)}")
    print(f"  Eye XML exists: {os.path.exists(eye_xml)}")
    
    if os.path.exists(face_xml):
        fc = cv2.CascadeClassifier(face_xml)
        print(f"  Face cascade loaded: {not fc.empty()}")
    
    if os.path.exists(eye_xml):
        ec = cv2.CascadeClassifier(eye_xml)
        print(f"  Eye cascade loaded: {not ec.empty()}")
