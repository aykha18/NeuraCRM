#!/usr/bin/env python3
"""
Build script to compile frontend and prepare for deployment
"""
import os
import subprocess
import sys

def build_frontend():
    """Build the React frontend"""
    print("Building frontend...")
    
    # Change to frontend directory
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    
    try:
        # Install dependencies
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "ci"], cwd=frontend_dir, check=True)
        
        # Build the frontend
        print("Building frontend for production...")
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        
        print("Frontend built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error building frontend: {e}")
        return False
    except FileNotFoundError:
        print("npm not found. Please install Node.js and npm.")
        return False

if __name__ == "__main__":
    success = build_frontend()
    sys.exit(0 if success else 1)
