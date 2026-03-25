# Driver Drowsiness Detection - Reference Values & Logic

## 📊 Research-Based Threshold Values

### 1. EAR (Eye Aspect Ratio)
Based on research papers (Soukupová & Čech, 2016):

```python
# EAR Reference Values
EAR_AWAKE = 0.25 - 0.35        # Normal, eyes open
EAR_BLINK = 0.15 - 0.25        # Quick blink
EAR_DROWSY = 0.15 - 0.20       # Eyes partially closed
EAR_SLEEPING = < 0.15          # Eyes fully closed

# Thresholds
EAR_THRESHOLD_DROWSY = 0.25    # Below this = drowsy
EAR_THRESHOLD_SLEEPING = 0.20  # Below this = sleeping
```

**How EAR Changes:**
- **Eyes Open (Focused)**: EAR = 0.28 - 0.35
- **Blinking**: EAR drops to 0.15-0.20 for 0.1-0.3 seconds
- **Drowsy**: EAR = 0.20 - 0.25 for 2+ seconds
- **Sleeping**: EAR < 0.20 for 3+ seconds

### 2. MAR (Mouth Aspect Ratio)
Based on yawning detection research:

```python
# MAR Reference Values
MAR_NORMAL = 0.05 - 0.15       # Mouth closed/slightly open
MAR_TALKING = 0.15 - 0.40      # Normal speech
MAR_YAWNING = > 0.50           # Yawning detected

# Thresholds
MAR_THRESHOLD_YAWN = 0.50      # Above this = yawning
```

**How MAR Changes:**
- **Mouth Closed**: MAR = 0.05 - 0.10
- **Talking**: MAR = 0.15 - 0.40 (fluctuates)
- **Yawning**: MAR > 0.50 for 1-3 seconds

### 3. Head Tilt (Degrees)
Based on head pose estimation:

```python
# Head Tilt Reference Values
TILT_NORMAL = -10° to +10°     # Straight ahead
TILT_SLIGHT = 10° to 20°       # Slight turn
TILT_DISTRACTED = > 20°        # Looking away

# Thresholds
TILT_THRESHOLD = 15°           # Above this = distracted
```

**How Head Tilt Changes:**
- **Focused**: -10° to +10°
- **Checking mirrors**: 15° - 30° (brief)
- **Distracted**: > 20° for 2+ seconds

### 4. Gaze Offset (Percentage)
Based on eye tracking research:

```python
# Gaze Offset Reference Values
GAZE_CENTER = 0% - 10%         # Looking at road
GAZE_PERIPHERAL = 10% - 25%    # Checking surroundings
GAZE_DISTRACTED = > 25%        # Not looking at road

# Thresholds
GAZE_THRESHOLD = 20%           # Above this = distracted
```

---

## 🧠 Production-Ready Detection Logic

### Complete State Classification Algorithm

```python
def classify_driver_state(ear, mar, head_tilt, gaze_offset, 
                         drowsy_frames, yawn_frames, distraction_frames):
    """
    Classify driver state based on multiple metrics with time-based filtering
    
    Args:
        ear: Eye Aspect Ratio (0.0 - 0.4)
        mar: Mouth Aspect Ratio (0.0 - 1.0)
        head_tilt: Head tilt angle in degrees
        gaze_offset: Gaze offset percentage
        drowsy_frames: Counter for consecutive drowsy frames
        yawn_frames: Counter for consecutive yawn frames
        distraction_frames: Counter for consecutive distraction frames
    
    Returns:
        dict: {status, confidence, ear, mar, head_tilt, gaze_offset}
    """
    
    # Thresholds
    EAR_DROWSY = 0.25
    EAR_SLEEPING = 0.20
    MAR_YAWN = 0.50
    TILT_DISTRACTED = 15
    GAZE_DISTRACTED = 20
    
    # Time thresholds (frames at 1 FPS)
    DROWSY_TIME = 2      # 2 seconds
    SLEEPING_TIME = 3    # 3 seconds
    YAWN_TIME = 1        # 1 second
    DISTRACTION_TIME = 2 # 2 seconds
    
    status = "focused"
    confidence = 0.7
    
    # Priority 1: SLEEPING (most critical)
    if ear < EAR_SLEEPING:
        drowsy_frames += 1
        if drowsy_frames >= SLEEPING_TIME:
            status = "sleeping"
            confidence = 0.95
            return {
                "status": status,
                "confidence": confidence,
                "ear": round(ear, 3),
                "mar": round(mar, 3),
                "head_tilt": round(head_tilt, 2),
                "gaze_offset": round(gaze_offset, 2),
                "alert_level": "CRITICAL"
            }
    
    # Priority 2: DROWSY
    if ear < EAR_DROWSY:
        drowsy_frames += 1
        if drowsy_frames >= DROWSY_TIME:
            status = "drowsy"
            confidence = 0.85
        elif drowsy_frames >= 1:
            status = "tired"
            confidence = 0.75
    else:
        drowsy_frames = 0
    
    # Priority 3: YAWNING (fatigue indicator)
    if mar > MAR_YAWN:
        yawn_frames += 1
        if yawn_frames >= YAWN_TIME and status == "focused":
            status = "yawning"
            confidence = 0.80
    else:
        yawn_frames = 0
    
    # Priority 4: DISTRACTION
    is_distracted = (
        abs(head_tilt) > TILT_DISTRACTED or 
        gaze_offset > GAZE_DISTRACTED
    )
    
    if is_distracted:
        distraction_frames += 1
        if distraction_frames >= DISTRACTION_TIME and status in ["focused", "tired"]:
            status = "distracted"
            confidence = 0.75
    else:
        distraction_frames = 0
    
    # Determine alert level
    alert_level = "NONE"
    if status == "sleeping":
        alert_level = "CRITICAL"
    elif status == "drowsy":
        alert_level = "HIGH"
    elif status in ["tired", "yawning"]:
        alert_level = "MEDIUM"
    elif status == "distracted":
        alert_level = "LOW"
    
    return {
        "status": status,
        "confidence": confidence,
        "ear": round(ear, 3),
        "mar": round(mar, 3),
        "head_tilt": round(head_tilt, 2),
        "gaze_offset": round(gaze_offset, 2),
        "alert_level": alert_level,
        "counters": {
            "drowsy_frames": drowsy_frames,
            "yawn_frames": yawn_frames,
            "distraction_frames": distraction_frames
        }
    }
```

---

## 📈 Expected Real-Time Behavior

### Scenario 1: Driver Gets Drowsy
```
Time | EAR   | Status      | Alert
-----|-------|-------------|-------
0s   | 0.30  | focused     | None
1s   | 0.28  | focused     | None
2s   | 0.24  | tired       | Low
3s   | 0.23  | drowsy      | High ⚠️
4s   | 0.22  | drowsy      | High ⚠️
5s   | 0.18  | sleeping    | CRITICAL 🚨
```

### Scenario 2: Driver Blinks (Normal)
```
Time | EAR   | Status      | Alert
-----|-------|-------------|-------
0s   | 0.30  | focused     | None
0.1s | 0.18  | focused     | None (too short)
0.3s | 0.30  | focused     | None
```

### Scenario 3: Driver Yawns
```
Time | MAR   | Status      | Alert
-----|-------|-------------|-------
0s   | 0.08  | focused     | None
1s   | 0.35  | focused     | None
2s   | 0.55  | yawning     | Medium 😴
3s   | 0.60  | yawning     | Medium 😴
4s   | 0.10  | focused     | None
```

### Scenario 4: Driver Looks Away
```
Time | Tilt  | Gaze  | Status      | Alert
-----|-------|-------|-------------|-------
0s   | 5°    | 8%    | focused     | None
1s   | 18°   | 25%   | focused     | None
2s   | 22°   | 30%   | distracted  | Low 👀
3s   | 25°   | 35%   | distracted  | Low 👀
4s   | 8°    | 10%   | focused     | None
```

---

## 🎯 Sample Output Examples

### Example 1: Focused Driver
```json
{
  "status": "focused",
  "confidence": 0.70,
  "ear": 0.305,
  "mar": 0.085,
  "head_tilt": 5.2,
  "gaze_offset": 8.5,
  "alert_level": "NONE",
  "faces": 1
}
```

### Example 2: Drowsy Driver
```json
{
  "status": "drowsy",
  "confidence": 0.85,
  "ear": 0.225,
  "mar": 0.095,
  "head_tilt": 3.8,
  "gaze_offset": 12.3,
  "alert_level": "HIGH",
  "faces": 1,
  "alert_message": "⚠️ DROWSINESS ALERT! Eyes are closing. Pull over and rest."
}
```

### Example 3: Sleeping Driver
```json
{
  "status": "sleeping",
  "confidence": 0.95,
  "ear": 0.180,
  "mar": 0.070,
  "head_tilt": 8.5,
  "gaze_offset": 15.2,
  "alert_level": "CRITICAL",
  "faces": 1,
  "alert_message": "🚨 CRITICAL: Driver appears to be sleeping! PULL OVER NOW!"
}
```

### Example 4: Yawning Driver
```json
{
  "status": "yawning",
  "confidence": 0.80,
  "ear": 0.285,
  "mar": 0.620,
  "head_tilt": 6.1,
  "gaze_offset": 9.8,
  "alert_level": "MEDIUM",
  "faces": 1,
  "alert_message": "😴 FATIGUE DETECTED! Frequent yawning. Consider taking a break."
}
```

### Example 5: Distracted Driver
```json
{
  "status": "distracted",
  "confidence": 0.75,
  "ear": 0.295,
  "mar": 0.105,
  "head_tilt": 22.5,
  "gaze_offset": 28.3,
  "alert_level": "LOW",
  "faces": 1,
  "alert_message": "👀 ATTENTION! Keep your eyes on the road ahead."
}
```

---

## ⚙️ Implementation Tips

### 1. Avoid False Positives
```python
# Use frame counters to filter noise
if ear < 0.25:
    drowsy_counter += 1
else:
    drowsy_counter = max(0, drowsy_counter - 1)  # Gradual decrease

# Only trigger alert after sustained detection
if drowsy_counter >= 2:  # 2 seconds at 1 FPS
    status = "drowsy"
```

### 2. Handle Blinks Correctly
```python
# Blinks are < 0.3 seconds, don't count as drowsy
if ear < 0.25 and previous_ear > 0.25:
    blink_start_time = current_time

if current_time - blink_start_time > 0.3:
    # Not a blink, count as drowsy
    drowsy_counter += 1
```

### 3. Smooth Transitions
```python
# Don't jump directly from focused to sleeping
# Use progressive states: focused → tired → drowsy → sleeping
```

### 4. Alert Prioritization
```python
# Priority order (highest to lowest):
# 1. Sleeping (CRITICAL)
# 2. Drowsy (HIGH)
# 3. Yawning (MEDIUM)
# 4. Distracted (LOW)
# 5. Tired (LOW)
```

---

## 📚 Research References

1. **EAR Thresholds**: Soukupová & Čech (2016) - "Real-Time Eye Blink Detection using Facial Landmarks"
2. **MAR for Yawning**: Abtahi et al. (2014) - "YawDD: A Yawning Detection Dataset"
3. **Head Pose**: Murphy-Chutorian & Trivedi (2009) - "Head Pose Estimation in Computer Vision"
4. **Drowsiness Detection**: Sahayadhas et al. (2012) - "Detecting Driver Drowsiness Based on Sensors"

---

## ✅ Validation Checklist

- [ ] EAR values range from 0.15 to 0.35
- [ ] MAR values range from 0.05 to 0.70
- [ ] Head tilt ranges from -30° to +30°
- [ ] Gaze offset ranges from 0% to 50%
- [ ] Drowsy triggers after 2 seconds
- [ ] Sleeping triggers after 3 seconds
- [ ] Yawning triggers after 1 second
- [ ] Distraction triggers after 2 seconds
- [ ] Blinks don't trigger false alerts
- [ ] Status transitions are smooth
- [ ] Alerts have proper priority levels

---

## 🚀 Next Steps

1. Implement the classification logic in your backend
2. Add frame counters for time-based detection
3. Test with real video footage
4. Calibrate thresholds based on your camera setup
5. Add logging to track detection accuracy
6. Implement alert system with different severity levels
