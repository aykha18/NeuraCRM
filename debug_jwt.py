import jwt
import os
from datetime import datetime, timedelta

def debug_jwt():
    # Test JWT creation and parsing
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    
    # Create a test token
    test_data = {
        "sub": "20",
        "user_id": 20,
        "organization_id": 8,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    
    print("Creating JWT token with data:")
    print(test_data)
    
    token = jwt.encode(test_data, SECRET_KEY, algorithm=ALGORITHM)
    print(f"\nGenerated token: {token}")
    
    # Decode the token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"\nDecoded payload: {payload}")
        
        # Test the logic from get_current_user
        user_id = payload.get("sub")
        print(f"\nuser_id from 'sub': {user_id}")
        print(f"user_id is digit: {str(user_id).isdigit()}")
        
        if not user_id or not str(user_id).isdigit():
            user_id = payload.get("user_id")
            print(f"user_id from 'user_id' field: {user_id}")
        
        print(f"Final user_id: {user_id}")
        
    except Exception as e:
        print(f"Error decoding token: {e}")

if __name__ == "__main__":
    debug_jwt()
