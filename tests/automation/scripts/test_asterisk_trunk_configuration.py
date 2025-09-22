#!/usr/bin/env python3
"""
Asterisk Trunk Configuration Test
Tests PBX provider configuration to match Asterisk trunk settings
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
LOGIN_EMAIL = "nodeit@node.com"
LOGIN_PASSWORD = "NodeIT2024!"

def login_and_get_token():
    """Login and get authentication token"""
    print("🔐 Logging in...")
    
    login_data = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print("✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def create_asterisk_trunk_configuration(token):
    """Create PBX provider configuration that matches Asterisk trunk settings"""
    print("\n🎯 CREATING ASTERISK TRUNK CONFIGURATION")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Configuration based on the images you showed
    # This matches the "Register Trunk" configuration from your FreePBX
    trunk_configs = [
        {
            "name": "Demo-telephone-Trunk",
            "provider_type": "asterisk",
            "display_name": "Demo Telephone Trunk",
            "description": "Asterisk trunk configuration for demo-telephone",
            "host": "your_asterisk_server_ip",  # Replace with your actual Asterisk server IP
            "port": 5060,  # Standard SIP port
            "username": "demo-telephone",  # This should match your trunk name
            "password": "your_trunk_password",  # Replace with your actual password
            "context": "from-trunk",  # Context for incoming calls
            "caller_id_field": "CallerIDNum",
            "dialplan_context": "from-internal",
            "recording_enabled": True,
            "recording_path": "/var/spool/asterisk/monitor",
            "transcription_enabled": False,
            "cdr_enabled": True,
            "cdr_path": "/var/log/asterisk/cdr-csv",
            "webhook_url": "",
            "webhook_secret": "",
            "auto_assign_calls": True,
            "is_active": True,
            "is_primary": True
        },
        {
            "name": "Register-Trunk-Config",
            "provider_type": "asterisk",
            "display_name": "Register Trunk Configuration",
            "description": "Asterisk register trunk with detailed configuration",
            "host": "your_asterisk_server_ip",  # Replace with your actual server IP
            "port": 5060,
            "username": "your_username",  # Authentication Name from your config
            "password": "your_password",  # Password from your config
            "context": "from-trunk",
            "caller_id_field": "CallerIDNum",
            "dialplan_context": "from-internal",
            "recording_enabled": True,
            "recording_path": "/var/spool/asterisk/monitor",
            "transcription_enabled": False,
            "cdr_enabled": True,
            "cdr_path": "/var/log/asterisk/cdr-csv",
            "webhook_url": "",
            "webhook_secret": "",
            "auto_assign_calls": True,
            "is_active": True,
            "is_primary": False
        }
    ]
    
    created_providers = []
    
    for i, config in enumerate(trunk_configs, 1):
        print(f"\n{i}. Creating trunk configuration: {config['name']}")
        print(f"   Host: {config['host']}")
        print(f"   Port: {config['port']}")
        print(f"   Username: {config['username']}")
        print(f"   Context: {config['context']}")
        
        response = requests.post(f"{BASE_URL}/api/telephony/providers", 
                               json=config, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            provider_id = result.get("id")
            created_providers.append(provider_id)
            print(f"✅ Trunk configuration created! ID: {provider_id}")
            print(f"   Name: {result.get('name')}")
            print(f"   Type: {result.get('provider_type')}")
            print(f"   Active: {result.get('is_active')}")
            print(f"   Primary: {result.get('is_primary')}")
        else:
            print(f"❌ Failed to create trunk configuration: {response.status_code}")
            print(f"   Error: {response.text}")
    
    return created_providers

def test_trunk_connection(token, provider_id):
    """Test connection to the trunk"""
    print(f"\n🔌 Testing trunk connection for provider ID: {provider_id}")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/api/telephony/providers/{provider_id}/test", 
                           headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Connection test completed!")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message')}")
        if result.get('response_time'):
            print(f"   Response time: {result.get('response_time')}ms")
        if result.get('error'):
            print(f"   Error: {result.get('error')}")
        return result.get('success', False)
    else:
        print(f"❌ Connection test failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def provide_asterisk_configuration_guide():
    """Provide detailed configuration guide for Asterisk trunk"""
    print("\n📋 ASTERISK TRUNK CONFIGURATION GUIDE")
    print("=" * 60)
    
    print("🔧 To fix the 'Demo-telephone' trunk registration issue:")
    print()
    print("1. **Check your Asterisk server configuration:**")
    print("   - Ensure your Asterisk server is running")
    print("   - Check if SIP port 5060 is open and accessible")
    print("   - Verify firewall settings")
    print()
    print("2. **Update the CRM PBX configuration with correct values:**")
    print("   - Host: Your actual Asterisk server IP address")
    print("   - Port: 5060 (or your custom SIP port)")
    print("   - Username: Should match your trunk name 'demo-telephone'")
    print("   - Password: Your actual trunk password")
    print("   - Context: 'from-trunk' for incoming calls")
    print()
    print("3. **Common Asterisk trunk configuration issues:**")
    print("   - Wrong hostname/IP address")
    print("   - Incorrect port number")
    print("   - Wrong username/password")
    print("   - Firewall blocking SIP traffic")
    print("   - Asterisk not running or misconfigured")
    print()
    print("4. **Check Asterisk logs for errors:**")
    print("   - /var/log/asterisk/full")
    print("   - /var/log/asterisk/messages")
    print("   - Look for SIP registration errors")
    print()
    print("5. **Verify FreePBX trunk settings:**")
    print("   - Trunk Type: Register Trunk")
    print("   - Hostname/IP: Your Asterisk server IP")
    print("   - Username: demo-telephone")
    print("   - Authentication Name: demo-telephone")
    print("   - Password: Your trunk password")
    print("   - Port: 5060")
    print("   - Transport: UDP")
    print()
    print("6. **Test connectivity:**")
    print("   - Ping your Asterisk server")
    print("   - Telnet to port 5060")
    print("   - Check SIP registration status")

def create_custom_trunk_configuration():
    """Create a custom trunk configuration template"""
    print("\n🛠️ CUSTOM TRUNK CONFIGURATION TEMPLATE")
    print("=" * 50)
    
    template = {
        "name": "YOUR_TRUNK_NAME",
        "provider_type": "asterisk",
        "display_name": "YOUR_DISPLAY_NAME",
        "description": "Custom trunk configuration",
        "host": "YOUR_ASTERISK_SERVER_IP",  # e.g., "192.168.1.100"
        "port": 5060,  # Standard SIP port
        "username": "YOUR_TRUNK_USERNAME",  # e.g., "demo-telephone"
        "password": "YOUR_TRUNK_PASSWORD",  # Your actual password
        "context": "from-trunk",  # Context for incoming calls
        "caller_id_field": "CallerIDNum",
        "dialplan_context": "from-internal",
        "recording_enabled": True,
        "recording_path": "/var/spool/asterisk/monitor",
        "transcription_enabled": False,
        "cdr_enabled": True,
        "cdr_path": "/var/log/asterisk/cdr-csv",
        "webhook_url": "",
        "webhook_secret": "",
        "auto_assign_calls": True,
        "is_active": True,
        "is_primary": True
    }
    
    print("📝 Use this template and replace the following values:")
    print(f"   YOUR_TRUNK_NAME: {template['name']}")
    print(f"   YOUR_DISPLAY_NAME: {template['display_name']}")
    print(f"   YOUR_ASTERISK_SERVER_IP: {template['host']}")
    print(f"   YOUR_TRUNK_USERNAME: {template['username']}")
    print(f"   YOUR_TRUNK_PASSWORD: {template['password']}")
    print()
    print("💡 Example with real values:")
    print("   name: 'demo-telephone'")
    print("   display_name: 'Demo Telephone Trunk'")
    print("   host: '192.168.1.100'")
    print("   username: 'demo-telephone'")
    print("   password: 'your_actual_password'")

def main():
    """Main test function"""
    print("🎯 ASTERISK TRUNK CONFIGURATION TEST")
    print("=" * 60)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login
    token = login_and_get_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    try:
        # Create trunk configurations
        created_providers = create_asterisk_trunk_configuration(token)
        
        # Test connections
        if created_providers:
            print(f"\n🔌 Testing connections for {len(created_providers)} providers...")
            for provider_id in created_providers:
                test_trunk_connection(token, provider_id)
        
        # Provide configuration guide
        provide_asterisk_configuration_guide()
        
        # Create custom template
        create_custom_trunk_configuration()
        
        print("\n🎉 ASTERISK TRUNK CONFIGURATION TEST COMPLETED!")
        print("=" * 60)
        print("✅ Trunk configurations created in CRM")
        print("✅ Connection tests performed")
        print("✅ Configuration guide provided")
        print()
        print("💡 NEXT STEPS:")
        print("   1. Update the host IP address with your actual Asterisk server IP")
        print("   2. Update the username to match your trunk name 'demo-telephone'")
        print("   3. Update the password with your actual trunk password")
        print("   4. Test the connection again")
        print("   5. Check your Asterisk server logs for any errors")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()



