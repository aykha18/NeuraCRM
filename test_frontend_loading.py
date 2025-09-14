#!/usr/bin/env python3
"""
Test frontend loading and identify the issue
"""
import requests
import time

def test_frontend_loading():
    """Test what's happening with the frontend"""
    url = "https://neuracrm.up.railway.app/"
    
    print("🔍 TESTING FRONTEND LOADING")
    print("="*60)
    
    try:
        # Test root page
        print("1️⃣ Testing root page...")
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            content = response.text
            print(f"   Content length: {len(content)}")
            
            # Check for key elements
            if '<title>' in content:
                title_start = content.find('<title>') + 7
                title_end = content.find('</title>')
                title = content[title_start:title_end]
                print(f"   Page title: {title}")
            
            if 'id="root"' in content:
                print("   ✅ React root div found")
            else:
                print("   ❌ React root div missing")
            
            if 'index-BxGQNkmq.js' in content:
                print("   ✅ Main JS file referenced")
            else:
                print("   ❌ Main JS file missing")
            
            if 'index-CUhkuEgz.css' in content:
                print("   ✅ Main CSS file referenced")
            else:
                print("   ❌ Main CSS file missing")
        
        # Test if JS and CSS files are accessible
        print("\n2️⃣ Testing static assets...")
        
        js_url = "https://neuracrm.up.railway.app/assets/index-BxGQNkmq.js"
        try:
            js_response = requests.get(js_url, timeout=5)
            print(f"   JS file: {js_response.status_code} ({len(js_response.content)} bytes)")
        except:
            print("   JS file: ❌ Not accessible")
        
        css_url = "https://neuracrm.up.railway.app/assets/index-CUhkuEgz.css"
        try:
            css_response = requests.get(css_url, timeout=5)
            print(f"   CSS file: {css_response.status_code} ({len(css_response.content)} bytes)")
        except:
            print("   CSS file: ❌ Not accessible")
        
        # Test API endpoints
        print("\n3️⃣ Testing API endpoints...")
        
        api_endpoints = [
            "/api/ping",
            "/api/health", 
            "/api/auth/login"
        ]
        
        for endpoint in api_endpoints:
            try:
                api_response = requests.get(f"https://neuracrm.up.railway.app{endpoint}", timeout=5)
                print(f"   {endpoint}: {api_response.status_code}")
            except:
                print(f"   {endpoint}: ❌ Not accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
        return False

def main():
    print("🚀 FRONTEND LOADING DIAGNOSIS")
    print("="*60)
    
    success = test_frontend_loading()
    
    print(f"\n{'='*60}")
    print("📋 DIAGNOSIS SUMMARY")
    print(f"{'='*60}")
    
    if success:
        print("✅ Frontend test completed")
        print("💡 Check the results above to identify the issue")
        print("💡 Common issues:")
        print("   - Missing static assets (JS/CSS files)")
        print("   - Frontend not building properly")
        print("   - API endpoints not responding")
        print("   - Database connection issues")
    else:
        print("❌ Frontend test failed")

if __name__ == "__main__":
    main()
