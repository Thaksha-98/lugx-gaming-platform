import requests
import sys

passed = 0
total = 2

# Test Game Service
try:
    r = requests.get("http://192.168.8.240/api/games")
    assert r.status_code == 200
    print("✅ Game Service OK")
    passed += 1
except:
    print("❌ Game Service Failed")

# Test Analytics Ingestion
try:
    r = requests.post("http://192.168.8.240/analytics", json={
        "timestamp": "2025-04-05T10:00:00Z",
        "page": "/test",
        "event_type": "test",
        "user_id": "test",
        "duration": 10,
        "scroll_depth": 50
    })
    assert r.status_code == 200
    print("✅ Analytics Ingestion OK")
    passed += 1
except:
    print("❌ Analytics Failed")

print(f"Tests: {passed}/{total}")
sys.exit(0 if passed == total else 1)
