#!/usr/bin/env python3
"""
Simple static file server for the frontend
"""
import os
import subprocess
import sys
from pathlib import Path

def build_and_serve_frontend():
    """Build the React frontend and serve it"""
    print("Building frontend...")
    
    # Change to frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        # Install dependencies
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "ci"], cwd=frontend_dir, check=True)
        
        # Build the frontend
        print("Building frontend for production...")
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        
        print("Frontend built successfully!")
        
        # Check if dist directory exists
        dist_dir = frontend_dir / "dist"
        if dist_dir.exists():
            print(f"Frontend built at: {dist_dir}")
            return True
        else:
            print("ERROR: dist directory not found after build")
            return False
        
    except subprocess.CalledProcessError as e:
        print(f"Error building frontend: {e}")
        return False
    except FileNotFoundError:
        print("npm not found. Please install Node.js and npm.")
        return False

if __name__ == "__main__":
    success = build_and_serve_frontend()
    sys.exit(0 if success else 1)
