#!/usr/bin/env python3
"""
Test Railway Authentication Dependencies
"""
import os
import sys

print("🔍 TESTING RAILWAY AUTHENTICATION DEPENDENCIES")
print("="*60)

# Test imports
try:
    from pydantic import EmailStr
    print("✅ EmailStr imported successfully")
except ImportError as e:
    print(f"❌ EmailStr import failed: {e}")

try:
    from passlib.context import CryptContext
    print("✅ CryptContext imported successfully")
except ImportError as e:
    print(f"❌ CryptContext import failed: {e}")

try:
    import jwt
    print("✅ JWT imported successfully")
except ImportError as e:
    print(f"❌ JWT import failed: {e}")

try:
    import bcrypt
    print("✅ bcrypt imported successfully")
except ImportError as e:
    print(f"❌ bcrypt import failed: {e}")

# Test environment variables
print(f"\n🔧 ENVIRONMENT VARIABLES:")
print(f"SECRET_KEY: {'Set' if os.getenv('SECRET_KEY') else 'Not set'}")
print(f"DATABASE_URL: {'Set' if os.getenv('DATABASE_URL') else 'Not set'}")

# Test database connection
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    from api.db import get_engine
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    print("✅ Database connection successful")
except Exception as e:
    print(f"❌ Database connection failed: {e}")

print("\n" + "="*60)
print("📋 SUMMARY")
print("="*60)
print("If all imports are successful, the authentication should work.")
print("If any imports fail, that's the root cause of the Railway auth issue.")
