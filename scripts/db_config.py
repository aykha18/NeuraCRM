"""
Database configuration utility for loading credentials from environment variables.
This module centralizes database connection configuration and ensures security.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_railway_db_config():
    """Get Railway database configuration from environment variables."""
    return {
        'host': os.getenv('RAILWAY_DB_HOST'),
        'database': os.getenv('RAILWAY_DB_DATABASE'),
        'user': os.getenv('RAILWAY_DB_USER'),
        'password': os.getenv('RAILWAY_DB_PASSWORD'),
        'port': int(os.getenv('RAILWAY_DB_PORT', 5432))
    }

def get_local_db_config():
    """Get local database configuration from environment variables."""
    return {
        'host': os.getenv('LOCAL_DB_HOST', 'localhost'),
        'database': os.getenv('LOCAL_DB_DATABASE', 'smart_crm'),
        'user': os.getenv('LOCAL_DB_USER', 'postgres'),
        'password': os.getenv('LOCAL_DB_PASSWORD', 'password'),
        'port': int(os.getenv('LOCAL_DB_PORT', 5432))
    }

def get_database_url(db_type='railway'):
    """Get database URL for connection."""
    if db_type == 'railway':
        config = get_railway_db_config()
    else:
        config = get_local_db_config()
    
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

def validate_config():
    """Validate that all required environment variables are set."""
    required_vars = [
        'RAILWAY_DB_HOST',
        'RAILWAY_DB_DATABASE', 
        'RAILWAY_DB_USER',
        'RAILWAY_DB_PASSWORD',
        'RAILWAY_DB_PORT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True
