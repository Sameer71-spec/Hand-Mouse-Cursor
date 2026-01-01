import mediapipe as mp
print(f"Version: {mp.__version__}")

try:
    import mediapipe.python.solutions
    print("Imported mediapipe.python.solutions")
except ImportError as e:
    print(f"Failed mediapipe.python.solutions: {e}")

try:
    from mediapipe import solutions
    print("From mediapipe import solutions SUCCESS")
except ImportError as e:
    print(f"Failed from mediapipe import solutions: {e}")

# Check if direct access works after import
try:
    print(f"mp.solutions: {mp.solutions}")
except AttributeError:
    print("mp.solutions still missing")
