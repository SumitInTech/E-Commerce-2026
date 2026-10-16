"""
Live Health & Integration Test Script for Snitch Luxe E-Commerce Microservices.
Run this script while the backend or microservices are running to verify end-to-end functionality.
Usage:
    python test_live_services.py
"""
import sys
import httpx
import json

GATEWAY_URL = "http://127.0.0.1:8000/api/v1"

SERVICES_TO_PING = [
    {"name": "API Gateway (Unified)", "url": "http://127.0.0.1:8000/api/v1/gateway/health", "expected": 200},
    {"name": "Auth Service (Autonomous)", "url": "http://127.0.0.1:8001/api/v1/auth/me", "expected": 401},  # 401 proves auth is active
    {"name": "Payment Service (Autonomous)", "url": "http://127.0.0.1:8002/docs", "expected": 200},
    {"name": "Catalog Service (Autonomous)", "url": "http://127.0.0.1:8003/api/v1/catalog/categories", "expected": 200},
    {"name": "Order Service (Autonomous)", "url": "http://127.0.0.1:8004/docs", "expected": 200},
    {"name": "Admin Service (Autonomous)", "url": "http://127.0.0.1:8005/docs", "expected": 200},
    {"name": "AI Fit Service (Autonomous)", "url": "http://127.0.0.1:8006/docs", "expected": 200},
    {"name": "Chatbot Service (Autonomous)", "url": "http://127.0.0.1:8007/docs", "expected": 200},
]


def test_gateway_and_endpoints():
    print("=" * 70)
    print("   SNITCH LUXE MICROSERVICES LIVE DIAGNOSTICS & SMOKE TEST")
    print("=" * 70)

    client = httpx.Client(timeout=5.0)

    # 1. Test Gateway Health
    print("\n[1] Testing Master API Gateway (Port 8000)...")
    try:
        r = client.get(f"{GATEWAY_URL}/gateway/health")
        if r.status_code == 200:
            data = r.json()
            print("    [PASS] API Gateway is HEALTHY! Status:", data.get("status"))
        else:
            print(f"    [FAIL] Gateway returned HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"    [OFFLINE] Could not reach Gateway on port 8000 ({e}).")
        print("    --> Did you start the server? Run: uvicorn backend.main:app --port 8000")
        return

    # 2. Test Auth Login (JWT Token)
    print("\n[2] Testing Auth Microservice (Login with Seeded Admin)...")
    token = None
    try:
        r = client.post(
            f"{GATEWAY_URL}/auth/login",
            json={"email": "admin@snitch.com", "password": "Admin@12345"}
        )
        if r.status_code == 200:
            token = r.json().get("access_token")
            role = r.json().get("role")
            print(f"    [PASS] Authentication Successful! Logged in as role: '{role}'")
        else:
            print(f"    [FAIL] Auth failed with HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"    [FAIL] Auth endpoint error: {e}")

    # 3. Test Catalog Microservice
    print("\n[3] Testing Catalog Microservice (Categories & Products)...")
    try:
        r = client.get(f"{GATEWAY_URL}/catalog/categories")
        if r.status_code == 200:
            cats = r.json()
            print(f"    [PASS] Successfully retrieved {len(cats)} Streetwear categories.")
        else:
            print(f"    [FAIL] Catalog categories returned HTTP {r.status_code}")

        r2 = client.get(f"{GATEWAY_URL}/catalog/products")
        if r2.status_code == 200:
            prods = r2.json()
            print(f"    [PASS] Successfully retrieved {len(prods)} Products with size charts.")
        else:
            print(f"    [FAIL] Products query returned HTTP {r2.status_code}")
    except Exception as e:
        print(f"    [FAIL] Catalog service error: {e}")

    # 4. Test AI Fit Sizing Engine
    print("\n[4] Testing AI Fit Sizing Engine (Kinematic Ease Recommendation)...")
    try:
        payload = {
            "chest_cm": 98.0,
            "waist_cm": 82.0,
            "hip_cm": 99.0,
            "garment_type": "shirt",
            "garment_specs": {"chest": 104, "waist": 88, "hip": 102},
            "fabric_stretch": "low"
        }
        r = client.post(f"{GATEWAY_URL}/ai/fit/recommend", json=payload)
        if r.status_code == 200:
            res = r.json()
            print(f"    [PASS] Sizing Engine Operational! Recommendation: {res.get('recommendation', 'Fit')} ({res.get('fit_category')})")
        else:
            print(f"    [FAIL] AI Fit returned HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"    [FAIL] AI Fit service error: {e}")

    # 5. Check Autonomous Port Health (if run_all_services.ps1 was used)
    print("\n[5] Scanning Individual Microservices Ports (8001 - 8007)...")
    for svc in SERVICES_TO_PING[1:]:
        try:
            r = client.get(svc["url"])
            if r.status_code in [200, 401]:
                print(f"    [UP] {svc['name']}: LIVE at {svc['url']}")
            else:
                print(f"    [WARN] {svc['name']}: HTTP {r.status_code}")
        except Exception:
            print(f"    [INACTIVE] {svc['name']}: Not running on dedicated port (Mounted via Gateway Port 8000)")

    print("\n" + "=" * 70)
    print("   DIAGNOSTICS COMPLETE!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_gateway_and_endpoints()
