import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_full_flow():
    print("1. Creating company profile...")
    company_data = {
        "name": "Trae Test Corp",
        "email": "test@trae.ai",
        "industry": "AI Tools",
        "description": "Testing the new crawler functionality",
        "website_url": "https://trae.ai"
    }
    resp = requests.post(f"{BASE_URL}/companies", json=company_data)
    if resp.status_code != 201:
        print(f"Failed to create company: {resp.text}")
        return
    
    company = resp.json()
    slug = company['slug']
    api_key = company['api_key']
    print(f"OK: Company created: {slug}")
    print(f"OK: API Key: {api_key}")

    print("\n2. Adding website source...")
    website_url = "https://docs.python.org/3/tutorial/index.html"
    resp = requests.post(
        f"{BASE_URL}/companies/{slug}/websites",
        headers={"X-API-Key": api_key},
        json={"url": website_url}
    )
    if resp.status_code != 200:
        print(f"Failed to add website: {resp.text}")
        return
    print(f"OK: Website added: {website_url}")

    print("\n3. Waiting for crawl to complete (15s)...")
    time.sleep(15)

    print("\n4. Checking knowledge base stats...")
    resp = requests.get(
        f"{BASE_URL}/knowledge/stats?company_slug={slug}",
        headers={"X-API-Key": api_key}
    )
    print(f"OK: KB Stats: {resp.json()}")

    print("\n5. Asking a question to the chatbot...")
    chat_data = {
        "message": "What is the Python tutorial about?",
        "company_slug": slug
    }
    resp = requests.post(f"{BASE_URL}/chat", json=chat_data)
    if resp.status_code != 200:
        print(f"Failed to ask question: {resp.text}")
        return
    
    chat_resp = resp.json()
    print(f"Bot Response: {chat_resp['response']}")
    print(f"Confidence: {chat_resp['confidence']}")
    print(f"Sources: {chat_resp['retrieved_sources']}")

if __name__ == "__main__":
    test_full_flow()
