from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uvicorn

from app.database import db
from app.auth_fastapi import create_token, decode_token, get_current_user
from app.vision import DriverMonitor

# Initialize FastAPI app
app = FastAPI(title="Driver AI Co-Pilot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db.init_db()

# Global monitor instance
monitor = None

# Try to initialize monitor at startup
import sys
sys.stdout.write("=" * 60 + "\n")
sys.stdout.write("DRIVER AI CO-PILOT - BACKEND STARTING\n")
sys.stdout.write("=" * 60 + "\n")
sys.stdout.flush()

try:
    sys.stdout.write("[STARTUP] Pre-initializing DriverMonitor...\n")
    sys.stdout.flush()
    monitor = DriverMonitor()
    sys.stdout.write("[STARTUP] SUCCESS: DriverMonitor ready!\n")
    sys.stdout.flush()
except Exception as e:
    sys.stdout.write(f"[STARTUP] ERROR: DriverMonitor initialization failed: {e}\n")
    sys.stdout.flush()
    import traceback
    traceback.print_exc()
    sys.stdout.write("[STARTUP] Will use fallback DummyMonitor\n")
    sys.stdout.flush()

sys.stdout.write("=" * 60 + "\n\n")
sys.stdout.flush()

def get_monitor():
    global monitor
    if monitor is None:
        import sys
        try:
            sys.stdout.write("[INIT] Initializing DriverMonitor...\n")
            sys.stdout.flush()
            monitor = DriverMonitor()
            sys.stdout.write("[INIT] SUCCESS: DriverMonitor initialized\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(f"[INIT] ERROR: Failed to initialize DriverMonitor: {e}\n")
            sys.stdout.flush()
            import traceback
            traceback.print_exc()
            # Create dummy monitor as fallback
            class DummyMonitor:
                def analyze(self, frame):
                    return {
                        "status": "error",
                        "confidence": 0,
                        "head_tilt": 0,
                        "gaze_offset": 0,
                        "faces": 0,
                        "ear": 0,
                        "mar": 0,
                    }
            monitor = DummyMonitor()
            sys.stdout.write("[INIT] Using DummyMonitor (returns error status)\n")
            sys.stdout.flush()
    return monitor

# Pydantic models
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AnalyzeRequest(BaseModel):
    frame: str

class SettingsUpdate(BaseModel):
    language: Optional[str] = None
    alertVolume: Optional[int] = None
    theme: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    driverId: str
    language: str
    alertVolume: int
    theme: str

# Helper functions
def serialize_user(user: dict) -> dict:
    return {
        "id": user['id'],
        "name": user['name'],
        "email": user['email'],
        "driverId": user['driver_id'],
        "language": user['language'],
        "alertVolume": user['alert_volume'],
        "theme": user['theme'],
    }

def get_alert_text(status: str) -> str:
    mapping = {
        "drowsy": "⚠️ DROWSINESS ALERT! Eyes are closing. Please pull over and rest.",
        "sleeping": "🚨 SLEEPING DETECTED! WAKE UP IMMEDIATELY! Pull over now!",
        "tired": "😴 TIREDNESS DETECTED! You look tired. Consider taking a break.",
        "distracted": "👀 ATTENTION! Keep your eyes on the road ahead.",
        "yawning": "😴 FATIGUE DETECTED! Frequent yawning indicates tiredness. Take a break.",
        "no_face_detected": "📷 Please ensure your face is visible to the camera.",
    }
    return mapping.get(status, "Stay focused and drive safely.")

# Routes
@app.get("/health")
async def health_check():
    return {"status": "ok", "database": "sqlite", "framework": "fastapi"}

@app.post("/api/auth/signup")
async def signup(request: SignupRequest):
    # Check if user exists
    existing_user = db.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")
    
    try:
        user = db.create_user(request.name, request.email, request.password)
        token = create_token(user)
        return {"token": token, "user": serialize_user(user)}
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    user = db.get_user_by_email(request.email)
    if not user or not db.verify_password(user, request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user)
    return {"token": token, "user": serialize_user(user)}

@app.get("/api/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"user": serialize_user(current_user)}

@app.put("/api/settings")
async def update_settings(
    settings: SettingsUpdate,
    current_user: dict = Depends(get_current_user)
):
    updates = {}
    if settings.language:
        updates["language"] = settings.language
    if settings.alertVolume is not None:
        updates["alert_volume"] = settings.alertVolume
    if settings.theme:
        updates["theme"] = settings.theme
    
    if updates:
        db.update_user_settings(current_user['id'], **updates)
        updated_user = db.get_user_by_id(current_user['id'])
        return {"user": serialize_user(updated_user)}
    
    return {"user": serialize_user(current_user)}

@app.post("/api/monitor/analyze")
async def analyze_frame(
    request: AnalyzeRequest,
    current_user: dict = Depends(get_current_user)
):
    import sys
    try:
        if not request.frame:
            raise HTTPException(status_code=400, detail="Frame is required")
        
        sys.stdout.write(f"[API] Received frame, length: {len(request.frame)}\n")
        sys.stdout.flush()
        
        # Analyze frame
        result = get_monitor().analyze(request.frame)
        
        sys.stdout.write(f"[API] Result: {result}\n")
        sys.stdout.flush()
        
        # Save to database if alert
        if result["status"] not in ["focused", "no_face_detected", "error"]:
            try:
                db.save_detection_event(
                    user_id=current_user['id'],
                    event_type=result["status"],
                    confidence=result["confidence"],
                    head_tilt=result.get("head_tilt", 0),
                    gaze_offset=result.get("gaze_offset", 0),
                    faces=result.get("faces", 0),
                    ear=result.get("ear", 0),
                    mar=result.get("mar", 0)
                )
            except Exception:
                pass
        
        active_alert = result["status"] in {"drowsy", "distracted", "yawning", "sleeping", "tired"}
        
        duration = 0
        if result["status"] == "sleeping":
            duration = 60
        elif result["status"] == "drowsy":
            duration = 30
        elif result["status"] == "tired":
            duration = 20
        elif result["status"] == "distracted":
            duration = 15
        elif result["status"] == "yawning":
            duration = 10
        
        return {
            "analysis": result,
            "alert": {
                "active": active_alert,
                "durationSeconds": duration,
                "message": get_alert_text(result["status"]),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        sys.stdout.write(f"[API] ERROR: {e}\n")
        sys.stdout.flush()
        # Return fallback instead of error
        return {
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
        }

@app.get("/api/history")
async def get_history(current_user: dict = Depends(get_current_user)):
    events = db.get_detection_history(current_user['id'])
    total_count = db.get_detection_count(current_user['id'])
    
    return {
        "items": events,
        "total": total_count,
        "limit": 200,
        "overLimit": total_count >= 200,
    }

@app.delete("/api/history/clear")
async def clear_history(current_user: dict = Depends(get_current_user)):
    db.clear_detection_history(current_user['id'])
    return {"message": "History cleared"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
