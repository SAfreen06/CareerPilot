# test_remotive_direct.py
import requests

response = requests.get("https://remotive.com/api/remote-jobs?search=python&limit=5")
print(f"Status: {response.status_code}")
data = response.json()
print(f"Jobs found: {len(data.get('jobs', []))}")
if data.get('jobs'):
    print(f"First job: {data['jobs'][0].get('title')}")