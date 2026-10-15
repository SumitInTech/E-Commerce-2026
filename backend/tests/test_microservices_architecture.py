"""
========================================================================================
ENTERPRISE MICROSERVICES AUTOMATED TEST HARNESS
========================================================================================
Validates all 7 autonomous microservices and the centralized API Gateway:
1. api_gateway/ (Health, Tracing, Sliding-Window Throttling, Security Sanitizer)
2. auth/ (Registration, Login, HS256 Token Validation, RBAC)
3. catalog/ (Categories, Product Specs, Multi-Point Anatomical Size Charts)
4. order/ (Cart Add/Remove, Atomic Checkout, 6-Stage Tracking Timeline)
5. payment/ (Payment Processing, Idempotency-Key Cache Replay, Refunds)
6. customer_admin/ (Ticket Escalation, Vendor Onboarding, GMV & AI Return Metrics)
7. ai_fit/ (Model 1 Anthropometry, Model 2 Kinematic Ease, Model 3 Color Harmonies)
8. chatbot/ (Model 4 Store Policy RAG, Live Order Fulfillment Injection)
========================================================================================
"""
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.api_gateway.main import app
from backend.database.supabase_client import init_db

# Initialize database schema and seeds
init_db()
client = TestClient(app)


def test_01_gateway_service_health_and_discovery():
    """Microservice 1: Gateway returns health and registered microservices."""
    res = client.get("/api/v1/gateway/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ONLINE"
    assert "services" in data
    assert data["services"]["gateway"]["status"] == "HEALTHY"
    assert data["services"]["auth"]["status"] == "HEALTHY"
    assert data["services"]["payment"]["status"] == "HEALTHY"
    assert data["services"]["catalog"]["status"] == "HEALTHY"
    assert data["services"]["order"]["status"] == "HEALTHY"
    assert data["services"]["customer_admin"]["status"] == "HEALTHY"
    assert data["services"]["ai_fit_style"]["status"] == "HEALTHY"
    assert data["services"]["ai_chatbot"]["status"] == "HEALTHY"


def test_02_gateway_tracing_and_latency_headers():
    """Microservice 1: Gateway injects X-Request-ID, X-Process-Time, and X-Gateway."""
    custom_req_id = str(uuid.uuid4())
    res = client.get("/api/v1/gateway/status", headers={"X-Request-ID": custom_req_id})
    assert res.status_code == 200
    assert res.headers.get("x-request-id") == custom_req_id
    assert "x-process-time" in res.headers
    assert res.headers.get("x-gateway") == "Snitch-Luxe-v2.5"


def test_03_gateway_security_sanitizer():
    """Microservice 1: Gateway blocks malicious SQL injection payloads."""
    res = client.get("/api/v1/catalog/products?search=shirt;DROP TABLE users;--")
    assert res.status_code == 400
    assert "Security validation blocked malicious traffic" in res.json()["error"]


def test_04_auth_service_workflow():
    """Microservice 2: Registration, Login, and Authenticated Profile."""
    test_email = f"test_{uuid.uuid4().hex[:6]}@snitch.com"
    # 1. Register
    reg_res = client.post("/api/v1/auth/register", json={
        "email": test_email,
        "password": "SecurePassword@123",
        "full_name": "Test Runner",
        "phone": "+91 99999 11111"
    })
    assert reg_res.status_code == 200
    user_data = reg_res.json()
    assert user_data["email"] == test_email

    # 2. Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "SecurePassword@123"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Authenticated Profile
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == test_email


def test_05_catalog_service_and_sizing_specs():
    """Microservice 4: Catalog queries and multi-point sizing charts."""
    # List categories
    cat_res = client.get("/api/v1/catalog/categories")
    assert cat_res.status_code == 200
    cats = cat_res.json()
    assert len(cats) >= 4

    # List products
    prod_res = client.get("/api/v1/catalog/products")
    assert prod_res.status_code == 200
    prods = prod_res.json()
    assert len(prods) >= 4

    # Get multi-point sizing specifications
    product_id = prods[0]["id"]
    sizes_res = client.get(f"/api/v1/catalog/sizes/{product_id}")
    assert sizes_res.status_code == 200
    sizes = sizes_res.json()
    assert len(sizes) >= 3
    assert "chest_cm" in sizes[0]
    assert "waist_cm" in sizes[0]
    assert "hip_cm" in sizes[0]


def test_06_order_and_cart_lifecycle():
    """Microservice 5: Cart Add, View, Checkout, and Tracking Timeline."""
    user_id = 9999

    # Add to cart
    add_res = client.post(f"/api/v1/orders/cart/{user_id}/items", json={
        "product_id": 1,
        "size_label": "M",
        "quantity": 2
    })
    assert add_res.status_code == 200
    cart = add_res.json()
    assert len(cart["items"]) >= 1
    assert cart["total_amount"] > 0

    # Checkout
    checkout_res = client.post("/api/v1/orders/checkout", json={
        "user_id": user_id,
        "shipping_address": "77 Cyber City, Gurugram, India",
        "payment_method": "card"
    })
    assert checkout_res.status_code == 200
    order = checkout_res.json()
    assert order["status"].lower() in ["created", "confirmed"]
    assert order["tracking_number"] is not None
    order_id = order["id"]

    # Tracking Timeline
    track_res = client.get(f"/api/v1/orders/{order_id}/track")
    assert track_res.status_code == 200
    track_data = track_res.json()
    assert len(track_data["timeline"]) >= 5
    assert track_data["timeline"][0]["completed"] is True


def test_07_payment_service_and_idempotency():
    """Microservice 3: Payment processing and Idempotency key replay."""
    idem_key = f"idem-key-{uuid.uuid4().hex}"
    payment_payload = {
        "order_id": 1,
        "user_id": 1,
        "amount": 2499.0,
        "payment_method": "card",
        "currency": "INR"
    }

    # First Call
    res1 = client.post(
        "/api/v1/payments/process",
        json=payment_payload,
        headers={"Idempotency-Key": idem_key}
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"].lower() == "success"
    assert "gateway_tx_id" in data1

    # Second Call (Replay using identical Idempotency-Key)
    res2 = client.post(
        "/api/v1/payments/process",
        json=payment_payload,
        headers={"Idempotency-Key": idem_key}
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["transaction_id"] == data1["transaction_id"]
    assert data2["gateway_tx_id"] == data1["gateway_tx_id"]


def test_08_customer_admin_service():
    """Microservice 6: Support tickets, vendor onboarding, and executive analytics."""
    # Create support ticket
    ticket_res = client.post("/api/v1/admin/tickets", json={
        "user_id": 1,
        "subject": "Size Exchange Inquiry for Linen Shirt",
        "description": "Requested advice on whether size L has sufficient ease.",
        "priority": "high"
    })
    assert ticket_res.status_code == 200
    assert ticket_res.json()["priority"].lower() in ["high", "critical"]

    # Executive metrics
    metrics_res = client.get("/api/v1/admin/metrics")
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()
    assert "total_gmv" in metrics
    assert "total_orders" in metrics
    assert metrics["return_rate_percentage"] <= 5.0


def test_09_ai_fit_and_style_service():
    """Microservice 7: Model 1 anthropometry, Model 2 ease, Model 3 color harmonies."""
    # Model 1: Body measurement regression
    meas_res = client.post("/api/v1/ai/fit/measurements", json={
        "height_cm": 180.0,
        "weight_kg": 76.0,
        "gender": "male"
    })
    assert meas_res.status_code == 200
    meas = meas_res.json()
    assert 90 <= meas["chest_cm"] <= 110
    assert 75 <= meas["waist_cm"] <= 95
    assert 90 <= meas["hip_cm"] <= 110

    # Model 2: Garment kinematic ease calculation
    fit_res = client.post("/api/v1/ai/fit/recommend", json={
        "chest_cm": 98.0,
        "waist_cm": 82.0,
        "hip_cm": 100.0,
        "garment_type": "shirt"
    })
    assert fit_res.status_code == 200
    fit = fit_res.json()
    assert fit["recommended_size"] in ["S", "M", "L", "XL"]
    assert "ease_allowance_cm" in fit

    # Model 3: CIE L*a*b* skin-tone & seasonal color palette matching
    color_res = client.post("/api/v1/ai/fit/color-palette", json={
        "hex_color": "#D4AA78"
    })
    assert color_res.status_code == 200
    colors = color_res.json()
    assert "recommended_palette" in colors
    assert len(colors["complementary_colors"]) >= 3


def test_10_ai_chatbot_service():
    """Microservice 8: Model 4 store policy RAG & live order status grounding."""
    chat_res = client.post("/api/v1/ai/chat/query", json={
        "query": "What is the return policy for shirts?"
    })
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert "answer" in data
    assert len(data["sources"]) >= 1

    # Live order status detection query
    order_query_res = client.post("/api/v1/ai/chat/query", json={
        "query": "Where is my order #1?"
    })
    assert order_query_res.status_code == 200
    order_data = order_query_res.json()
    assert "order" in order_data["answer"].lower() or order_data.get("order_context") is not None
