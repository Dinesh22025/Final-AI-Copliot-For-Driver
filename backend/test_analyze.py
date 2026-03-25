import sys
import base64
from app.vision import DriverMonitor

# Create a simple test image (1x1 black pixel)
test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

# Encode as base64 like the frontend does
base64_image = "data:image/png;base64," + base64.b64encode(test_image_data).decode('utf-8')

print("Testing DriverMonitor with base64 image...")
print(f"Image data length: {len(base64_image)}")

try:
    monitor = DriverMonitor()
    print("DriverMonitor initialized")
    
    result = monitor.analyze(base64_image)
    print(f"Analysis result: {result}")
    print("SUCCESS!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
