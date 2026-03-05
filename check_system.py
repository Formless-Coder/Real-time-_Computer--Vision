#!/usr/bin/env python3
"""
System Check Script - Verify all dependencies and system requirements
Run this to diagnose issues before launching the main application
"""

import sys
import subprocess
import os

print("🔍 System Check for Real-time Computer Vision Project")
print("=" * 60)
print()

checks_passed = 0
checks_total = 0

def check_python_version():
    """Verify Python 3.8+"""
    global checks_passed, checks_total
    checks_total += 1
    
    print(f"[{checks_total}] Python Version:", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        checks_passed += 1
    else:
        print(f"❌ Python {version.major}.{version.minor} (Need 3.8+)")

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    global checks_passed, checks_total
    checks_total += 1
    
    if import_name is None:
        import_name = package_name
    
    print(f"[{checks_total}] {package_name}:", end=" ")
    try:
        __import__(import_name)
        # Get version if available
        try:
            version = __import__(import_name).__version__
            print(f"✅ {version}")
        except AttributeError:
            print("✅ Installed")
        checks_passed += 1
    except ImportError:
        print(f"❌ Not installed (pip install {package_name})")

def check_camera():
    """Check if camera device exists"""
    global checks_passed, checks_total
    checks_total += 1
    
    print(f"[{checks_total}] Camera Device:", end=" ")
    
    # Try to open camera with OpenCV
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.release()
            print("✅ Camera accessible")
            checks_passed += 1
        else:
            print("❌ Camera not accessible (check permissions)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_osascript():
    """Check if osascript (AppleScript) is available"""
    global checks_passed, checks_total
    checks_total += 1
    
    print(f"[{checks_total}] osascript (macOS):", end=" ")
    try:
        result = subprocess.run(['which', 'osascript'], capture_output=True)
        if result.returncode == 0:
            print("✅ Available")
            checks_passed += 1
        else:
            print("❌ Not found (macOS required)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_volume_control():
    """Test volume control with osascript"""
    global checks_passed, checks_total
    checks_total += 1
    
    print(f"[{checks_total}] Volume Control Test:", end=" ")
    try:
        # Get current volume first
        result = subprocess.run(
            ['osascript', '-e', 'get volume output volume'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Volume level: {result.stdout.strip()}%")
            checks_passed += 1
        else:
            print("❌ Failed to read volume")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_directory_structure():
    """Verify project directory structure"""
    global checks_passed, checks_total
    checks_total += 1
    
    print(f"[{checks_total}] Directory Structure:", end=" ")
    required_dirs = ['templates', 'static']
    required_files = ['app.py', 'requirements.txt']
    
    missing = []
    for d in required_dirs:
        if not os.path.isdir(d):
            missing.append(f"📁 {d}/")
    for f in required_files:
        if not os.path.isfile(f):
            missing.append(f"📄 {f}")
    
    if not missing:
        print("✅ All files present")
        checks_passed += 1
    else:
        print(f"❌ Missing: {', '.join(missing)}")

def check_flask_port():
    """Check if default port (5001) is available"""
    global checks_passed, checks_total
    checks_total += 1
    
    print(f"[{checks_total}] Port 5001 Available:", end=" ")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 5001))
        sock.close()
        
        if result != 0:
            print("✅ Port available")
            checks_passed += 1
        else:
            print("⚠️  Port 5001 in use (you can use different port)")
            checks_passed += 1  # Still passing
    except Exception as e:
        print(f"⚠️  Could not check: {str(e)}")

# Run all checks
print("Running diagnostics...\n")

check_python_version()
check_package("Flask")
check_package("OpenCV", "cv2")
check_package("MediaPipe", "mediapipe")
check_package("NumPy", "numpy")
check_package("Werkzeug")

print()

check_directory_structure()
check_camera()
check_osascript()
check_volume_control()
check_flask_port()

# Summary
print()
print("=" * 60)
print(f"Results: {checks_passed}/{checks_total} checks passed")
print("=" * 60)
print()

if checks_passed == checks_total:
    print("✅ All systems ready! You can start the application:")
    print("   python app.py")
elif checks_passed >= checks_total - 1:
    print("⚠️  Most checks passed. Some features may not work optimally.")
    print("   Try running 'python app.py' to see if there are issues.")
else:
    print("❌ Some critical issues detected. Please resolve them first:")
    print("   1. Install missing Python packages: pip install -r requirements.txt")
    print("   2. Grant camera permissions in System Preferences")
    print("   3. Ensure you're running on macOS with osascript available")

print()
