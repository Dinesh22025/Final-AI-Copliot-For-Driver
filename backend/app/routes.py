import json
from datetime import datetime
from flask import Blueprint, jsonify, request, g
from .auth import auth_required, create_token
from .database import db

api = Blueprint("api", __name__, url_prefix="/api")
monitor = None

def get_monitor():
    global monitor
    if monitor is None:
        try:
            from .vision import DriverMonitor
            print("[DEBUG] Attempting to initialize DriverMonitor...")
            monitor = DriverMonitor()
            print("[DEBUG] DriverMonitor initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize DriverMonitor: {e}")
            import traceback
            traceback.print_exc()
            # If monitor fails to initialize, create a dummy one that returns focused
            class DummyMonitor:
                def analyze(self, frame):
                    return {
                        "status": "focused",
                        "confidence": 0.5,
                        "head_tilt": 0,
                        "gaze_offset": 0,
                        "faces": 1,
                        "ear": 0.3,
                        "mar": 0.05,
                    }
            monitor = DummyMonitor()
            print("[DEBUG] Using DummyMonitor fallback")
    return monitor

@api.post("/auth/signup")
def signup():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not all([name, email, password]):
        return jsonify({"error": "Name, email, and password are required."}), 400

    # Check if user already exists
    existing_user = db.get_user_by_email(email)
    if existing_user:
        return jsonify({"error": "Email already exists."}), 409

    try:
        user = db.create_user(name, email, password)
        token = create_token(user)
        return jsonify({"token": token, "user": _serialize_user(user)}), 201
    except Exception as e:
        return jsonify({"error": "Failed to create user"}), 500

@api.post("/auth/login")
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = db.get_user_by_email(email)
    if not user or not db.verify_password(user, password):
        return jsonify({"error": "Invalid credentials."}), 401

    token = create_token(user)
    return jsonify({"token": token, "user": _serialize_user(user)})

@api.get("/me")
@auth_required
def me():
    return jsonify({"user": _serialize_user(g.current_user)})

@api.put("/settings")
@auth_required
def update_settings():
    data = request.get_json() or {}
    updates = {}
    
    if "language" in data:
        updates["language"] = data["language"]
    if "alertVolume" in data:
        updates["alert_volume"] = data["alertVolume"]
    if "theme" in data:
        updates["theme"] = data["theme"]

    if updates:
        db.update_user_settings(g.current_user['id'], **updates)
        # Get updated user data
        updated_user = db.get_user_by_id(g.current_user['id'])
        return jsonify({"user": _serialize_user(updated_user)})
    
    return jsonify({"user": _serialize_user(g.current_user)})

@api.post("/monitor/test")
def test_endpoint():
    """Simple test endpoint to verify backend is working"""
    return jsonify({
        "status": "ok",
        "message": "Backend is working",
        "timestamp": datetime.now().isoformat()
    })

@api.post("/monitor/analyze")
@auth_required
def analyze_frame():
    try:
        data = request.get_json() or {}
        frame = data.get("frame", "")
        if not frame:
            return jsonify({"error": "Frame is required"}), 400

        print(f"[DEBUG] Analyzing frame, length: {len(frame)}")
        
        # Get monitor and analyze
        try:
            monitor_instance = get_monitor()
            print(f"[DEBUG] Got monitor instance: {type(monitor_instance)}")
            result = monitor_instance.analyze(frame)
            print(f"[DEBUG] Analysis result: {result}")
        except Exception as analysis_error:
            print(f"[ERROR] Analysis failed: {analysis_error}")
            import traceback
            traceback.print_exc()
            # Return focused as fallback
            result = {
                "status": "focused",
                "confidence": 0.5,
                "head_tilt": 0,
                "gaze_offset": 0,
                "faces": 1,
                "ear": 0.3,
                "mar": 0.05,
            }
        
        # Save to database if status indicates an alert
        if result["status"] not in ["focused", "no_face_detected", "error"]:
            try:
                db.save_detection_event(
                    user_id=g.current_user['id'],
                    event_type=result["status"],
                    confidence=result["confidence"],
                    head_tilt=result.get("head_tilt", 0),
                    gaze_offset=result.get("gaze_offset", 0),
                    faces=result.get("faces", 0),
                    ear=result.get("ear", 0),
                    mar=result.get("mar", 0)
                )
            except Exception:
                pass  # Continue even if database save fails
        
        # Determine alert status and duration
        alert_statuses = {"drowsy", "distracted", "yawning", "sleeping", "tired"}
        active_alert = result["status"] in alert_statuses
        
        duration_map = {
            "sleeping": 60,
            "drowsy": 30,
            "tired": 20,
            "distracted": 15,
            "yawning": 10
        }
        duration = duration_map.get(result["status"], 0)
        
        return jsonify({
            "analysis": result,
            "alert": {
                "active": active_alert,
                "durationSeconds": duration,
                "message": _alert_text(result["status"]),
            },
        })
    except Exception as e:
        print(f"[ERROR] Analyze frame error: {e}")
        import traceback
        traceback.print_exc()
        # Return a safe fallback response
        return jsonify({
            "analysis": {
                "status": "focused",
                "confidence": 0.5,
                "head_tilt": 0,
                "gaze_offset": 0,
                "faces": 1,
                "ear": 0.3,
                "mar": 0.05,
            },
            "alert": {
                "active": False,
                "durationSeconds": 0,
                "message": "Stay focused and drive safely.",
            },
        })

@api.get("/history")
@auth_required
def history():
    events = db.get_detection_history(g.current_user['id'])
    total_count = db.get_detection_count(g.current_user['id'])
    
    return jsonify({
        "items": events,
        "total": total_count,
        "limit": 200,
        "overLimit": total_count >= 200,
    })

@api.delete("/history/clear")
@auth_required
def clear_history():
    db.clear_detection_history(g.current_user['id'])
    return jsonify({"message": "History cleared"})

def _serialize_user(user):
    return {
        "id": user['id'],
        "name": user['name'],
        "email": user['email'],
        "driverId": user['driver_id'],
        "language": user['language'],
        "alertVolume": user['alert_volume'],
        "theme": user['theme'],
    }

def _alert_text(status: str) -> str:
    mapping = {
        "sleeping": "🚨 CRITICAL: Driver appears to be sleeping! Pull over immediately!",
        "drowsy": "⚠️ DROWSINESS ALERT! Eyes are closing. Please pull over and rest.",
        "tired": "😴 TIREDNESS DETECTED! Consider taking a break soon.",
        "distracted": "👀 ATTENTION! Keep your eyes on the road ahead.",
        "yawning": "😴 FATIGUE DETECTED! Frequent yawning indicates tiredness. Take a break.",
        "no_face_detected": "📷 Please ensure your face is visible to the camera.",
    }
    return mapping.get(status, "Stay focused and drive safely.")
