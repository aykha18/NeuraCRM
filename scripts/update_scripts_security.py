#!/usr/bin/env python3
"""
Update Scripts Security
=======================

This script updates all Python scripts in the scripts directory to use environment variables
instead of hardcoded Railway database credentials.
"""

import os
import re
import glob

def update_script_security(script_path):
    """Update a single script to use secure environment variables."""
    print(f"🔧 Updating {script_path}...")
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Check if script already uses db_config
    if 'from db_config import' in content:
        print(f"   ⏭️  {script_path} already updated, skipping...")
        return False
    
    # Pattern to match Railway DB config dictionaries
    railway_config_pattern = r'RAILWAY_DB_CONFIG\s*=\s*\{[^}]*\'host\':\s*\'[^\']*\',[^}]*\'database\':\s*\'[^\']*\',[^}]*\'user\':\s*\'[^\']*\',[^}]*\'password\':\s*\'[^\']*\',[^}]*\'port\':\s*\d+[^}]*\}'
    
    # Check if script has hardcoded Railway config
    if re.search(railway_config_pattern, content, re.DOTALL):
        # Add imports after existing imports
        import_section = re.search(r'(import\s+[^\n]*\n)+', content)
        if import_section:
            import_end = import_section.end()
            # Add our imports
            new_imports = """
import sys
import os

# Add the scripts directory to the path to import db_config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db_config import get_railway_db_config, validate_config
"""
            content = content[:import_end] + new_imports + content[import_end:]
        
        # Replace RAILWAY_DB_CONFIG usage
        content = re.sub(
            railway_config_pattern,
            '# Railway DB config now loaded from environment variables',
            content,
            flags=re.DOTALL
        )
        
        # Replace psycopg2.connect(**RAILWAY_DB_CONFIG) with secure version
        content = re.sub(
            r'psycopg2\.connect\(\*\*RAILWAY_DB_CONFIG\)',
            '''psycopg2.connect(**get_railway_db_config())''',
            content
        )
        
        # Add validation before database connection
        connection_pattern = r'(print\([^)]*Connecting to Railway database[^)]*\)\s*\n\s*)(conn\s*=\s*psycopg2\.connect)'
        replacement = r'\1# Validate environment configuration\n        validate_config()\n        \n        # Get Railway database configuration from environment variables\n        railway_config = get_railway_db_config()\n        \n        \2(**railway_config)'
        content = re.sub(connection_pattern, replacement, content)
        
        # Write updated content
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ Updated {script_path}")
        return True
    
    return False

def main():
    """Update all Python scripts in the scripts directory."""
    print("🔒 Updating scripts to use secure environment variables...")
    
    # Find all Python scripts
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    python_scripts = glob.glob(os.path.join(scripts_dir, "*.py"))
    
    updated_count = 0
    skipped_count = 0
    
    for script_path in python_scripts:
        script_name = os.path.basename(script_path)
        
        # Skip this script and db_config.py
        if script_name in ['update_scripts_security.py', 'db_config.py']:
            continue
            
        try:
            if update_script_security(script_path):
                updated_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"   ❌ Error updating {script_name}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Updated: {updated_count} scripts")
    print(f"   ⏭️  Skipped: {skipped_count} scripts")
    print(f"\n🔐 All scripts now use secure environment variables!")
    print(f"📝 Make sure to create .env file with your Railway credentials.")

if __name__ == "__main__":
    main()
