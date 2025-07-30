import requests
import sys
import argparse

def run_test(target):
    base_url = "http://192.168.8.240"
    
    try:
        r = requests.get(f"{base_url}/", timeout=10)
        assert r.status_code == 200
        print("✅ Homepage loads")
    except Exception as e:
        print("❌ Homepage failed:", e)
        sys.exit(1)

    try:
        r = requests.post(f"{base_url}/analytics", json={
            "timestamp": "2025-04-05T10:00:00Z",
            "page": "/test",
            "event_type": f"test-{target}",
            "user_id": "test",
            "duration": 10,
            "scroll_depth": 50
        }, timeout=10)
        assert r.status_code == 200
        print(f"✅ Analytics sent to {target}")
    except Exception as e:
        print("❌ Analytics failed:", e)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', default='unknown')
    args = parser.parse_args()
    run_test(args.target)
