import requests, sys, json
BASE='http://127.0.0.1:8000'
EMAIL='nodeit@node.com'
PASSWORD='NodeIT2024!'

def main():
    print('1) login')
    r=requests.post(f"{BASE}/api/auth/login", json={'email':EMAIL,'password':PASSWORD})
    print(' login', r.status_code)
    if r.status_code!=200:
        print(r.text); sys.exit(1)
    token=r.json()['access_token']
    h={'Authorization': f'Bearer {token}'}

    print('2) GET /chat/rooms')
    r=requests.get(f"{BASE}/chat/rooms", headers=h)
    print(' rooms', r.status_code, len(r.json()) if r.status_code==200 else r.text)
    
    print('3) GET org users')
    me=requests.get(f"{BASE}/api/auth/me", headers=h).json()
    org_id=me['organization_id']
    r=requests.get(f"{BASE}/chat/organizations/{org_id}/users", headers=h)
    print(' users', r.status_code, (len(r.json()) if r.status_code==200 else r.text))

    print('4) POST /chat/rooms')
    body={
        'name':'Auto Room',
        'description':'Automated test',
        'room_type':'group',
        'organization_id': org_id,
        'participant_ids': []
    }
    r=requests.post(f"{BASE}/chat/rooms", headers=h, json=body)
    print(' create', r.status_code)
    if r.status_code!=200:
        print(r.text); sys.exit(1)
    room=r.json(); room_id=room['id']

    print('5) GET messages (empty ok)')
    r=requests.get(f"{BASE}/chat/rooms/{room_id}/messages", headers=h)
    print(' messages', r.status_code, (len(r.json()) if r.status_code==200 else r.text))

    print('6) POST message')
    r=requests.post(f"{BASE}/chat/rooms/{room_id}/messages", headers=h, json={'content':'Hello from test!'})
    print(' send', r.status_code)
    if r.status_code!=200:
        print(r.text); sys.exit(1)

    print('7) GET messages again')
    r=requests.get(f"{BASE}/chat/rooms/{room_id}/messages", headers=h)
    print(' messages', r.status_code, (len(r.json()) if r.status_code==200 else r.text))

    print('OK')

if __name__=='__main__':
    main()
