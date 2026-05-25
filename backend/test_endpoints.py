import requests
import json

BASE_URL = "http://localhost:8000"

print("Testing /api/chat/stream...")
payload = {
    "session_id": "test-session-123",
    "message": "Hello, how are you?",
    "company_slug": "demo-corp"
}
response = requests.post(f"{BASE_URL}/api/chat/stream", json=payload, stream=True)
print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")

if response.status_code == 200:
    print("\nStreaming response:")
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
else:
    print(f"\nError response: {response.text}")
