"""
Quick Start Script
Runs both backend and frontend.
"""
import subprocess
import sys
import time
from pathlib import Path

def main():
    """Run backend and frontend."""
    root = Path(__file__).parent
    backend_dir = root / "backend"
    frontend_dir = root / "frontend"
    
    print("🚀 Starting Budget Analyst...")
    print()
    
    # Start backend
    print("📡 Starting backend (FastAPI)...")
    backend_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Wait for backend to start
    time.sleep(3)
    
    # Start frontend
    print("🎨 Starting frontend (Streamlit)...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        cwd=frontend_dir,
    )
    
    print()
    print("✅ Both services running!")
    print()
    print("📡 Backend: http://localhost:8000")
    print("🎨 Frontend: http://localhost:8501")
    print()
    print("Press Ctrl+C to stop both services")
    
    try:
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("✅ Services stopped")

if __name__ == "__main__":
    main()
