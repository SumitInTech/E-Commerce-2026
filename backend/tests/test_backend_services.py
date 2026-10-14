"""
Comprehensive Automated Test Suite for Backend Platform Microservices.
Verifies all 7 Enterprise Platform Services:
1. API Gateway Service (Health, CORS, Request-ID, Process-Time)
2. Auth Service (Registration, Login, Role-Based Access)
3. Payment Service (Idempotency, Gateway Processing, Transactions)
4. Order & Catalog Service (Product queries, Size charts, Cart, Checkout, Order Tracking)
5. Customer & Admin Service (Ticketing workflow, Vendor applications, Business metrics)
6. AI Fit & Style Service (Biometric regression, Garment ease analysis, Seasonal color harmonies)
7. AI Chatbot Service (RAG store policy, Citations, Order fulfillment lookup)
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import init_db

# Initialize database schema and seeds
init_db()
client = TestClient(app)


def test_01_gateway_health():
    """Service 1: API Gateway health endpoint returns status of all 7 services."""
    response = client.get("/api/v1/gateway/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert "services" in data
    assert data["services"]["gateway"]["status"] == "HEALTHY"
    assert data["services"]["auth"]["status"] == "HEALTHY"
    assert data["services"]["payment"]["status"] == "HEALTHY"
    assert data["services"]["catalog_order"]["status"] == "HEALTHY"
    assert data["services"]["customer_admin"]["status"] == "HEALTHY"
    assert data["services"]["ai_fit_style"]["status"] == "HEALTHY"
    assert data["services"]["ai_chatbot"]["status"] == "HEALTHY"


def test_02_gateway_headers():
    """Service 1: API Gateway attaches X-Request-ID and X-Process-Time headers."""
    response = client.get("/api/v1/gateway/status")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert "x-process-time" in response.headers


def test_03_auth_login():
    """Service 2: Auth Service verifies credentials and issues signed JWT."""
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@snitch.com",
        "password": "Admin@12345"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["email"] == "admin@snitch.com"


def test_04_auth_register_and_profile():
    """Service 2: Auth Service registers new buyer and accesses profile via Bearer token."""
    import uuid
    unique_email = f"buyer_{uuid.uuid4().hex[:8]}@snitch.com"
    reg_response = client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "Password@123",
        "full_name": "Test Customer",
        "role": "buyer",
        "phone": "+91 99999 11111"
    })
    assert reg_response.status_code == 200
    token = reg_response.json()["access_token"]

    profile_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == unique_email


def test_05_catalog_categories_and_products():
    """Service 4: Catalog Service returns categories and products with complete size charts."""
    cat_res = client.get("/api/v1/catalog/categories")
    assert cat_res.status_code == 200
    assert len(cat_res.json()) >= 4

    prod_res = client.get("/api/v1/catalog/products")
    assert prod_res.status_code == 200
    products = prod_res.json()
    assert len(products) >= 6

    # Verify first product has size chart
    p1 = products[0]
    assert len(p1["sizes"]) >= 3
    assert p1["sizes"][0]["chest_cm"] is not None


def test_06_cart_and_checkout_lifecycle():
    """Service 4: Order Service cart additions and checkout transition to confirmed order."""
    session_id = "cart_test_session_9921"

    # Add to cart
    add_res = client.post(f"/api/v1/orders/cart/add?session_id={session_id}", json={
        "product_id": 1,
        "size_label": "M",
        "quantity": 1
    })
    assert add_res.status_code == 200
    cart_data = add_res.json()
    assert len(cart_data["items"]) >= 1
    assert cart_data["subtotal"] > 0

    # Checkout
    checkout_res = client.post("/api/v1/orders/checkout", json={
        "customer_name": "Vikram Seth",
        "customer_email": "vikram@example.com",
        "shipping_address": "Flat 3B, Jubilee Hills, Hyderabad",
        "payment_method": "UPI",
        "cart_items": [{"product_id": 1, "size_label": "M", "quantity": 1}]
    })
    assert checkout_res.status_code == 200
    order_data = checkout_res.json()
    assert order_data["order_number"].startswith("ORD-SNITCH-")
    assert order_data["status"] == "confirmed"

    # Track order
    track_res = client.get(f"/api/v1/orders/track/{order_data['order_number']}")
    assert track_res.status_code == 200
    assert track_res.json()["tracking_number"] is not None


def test_07_payment_with_idempotency():
    """Service 3: Payment Service guarantees idempotency and processes transactions."""
    idempotency_key = "idem_test_key_abc_123"

    res1 = client.post(
        "/api/v1/payments/process",
        json={"order_id": 1, "amount": 1899.0, "method": "CARD"},
        headers={"Idempotency-Key": idempotency_key}
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "success"
    assert "transaction_id" in data1

    # Second call with identical key must return cached record with identical transaction_id
    res2 = client.post(
        "/api/v1/payments/process",
        json={"order_id": 1, "amount": 1899.0, "method": "CARD"},
        headers={"Idempotency-Key": idempotency_key}
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["transaction_id"] == data1["transaction_id"]


def test_08_admin_metrics_and_tickets():
    """Service 5: Customer & Admin Service calculates metrics and manages support tickets."""
    # Metrics
    m_res = client.get("/api/v1/admin/metrics")
    assert m_res.status_code == 200
    assert m_res.json()["total_sales_revenue"] > 0

    # Submit ticket
    t_res = client.post("/api/v1/admin/tickets", json={
        "customer_name": "Devin Roy",
        "customer_email": "devin@example.com",
        "subject": "Size fit question for Korean Trousers",
        "message": "Does the waist run true to size or should I size down?",
        "priority": "low"
    })
    assert t_res.status_code == 200
    ticket_id = t_res.json()["id"]

    # Update ticket
    patch_res = client.patch(f"/api/v1/admin/tickets/{ticket_id}", json={
        "status": "in_progress",
        "admin_notes": "Advised true to size based on pleated silhouette."
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "in_progress"


def test_09_ai_fit_predictions():
    """Service 6: AI Fit & Style Service predicts measurements and evaluates kinematic ease."""
    # Model 1 Biometrics
    m1_res = client.post("/api/v1/ai-fit/predict-measurements", json={
        "height_cm": 178.0,
        "weight_kg": 75.0,
        "gender": "male"
    })
    assert m1_res.status_code == 200
    preds = m1_res.json()["predictions"]
    assert 85.0 <= preds["chest_cm"] <= 120.0
    assert 70.0 <= preds["waist_cm"] <= 115.0

    # Model 2 Fit evaluation against Product 1
    m2_res = client.post("/api/v1/ai-fit/evaluate-garment-fit", json={
        "chest_cm": preds["chest_cm"],
        "waist_cm": preds["waist_cm"],
        "hip_cm": preds["hip_cm"],
        "product_id": 1
    })
    assert m2_res.status_code == 200
    fit_data = m2_res.json()
    assert fit_data["recommended_size"] in ["S", "M", "L", "XL", "XXL"]
    assert fit_data["primary_ease_cm"] is not None

    # Model 3 Color Harmonies
    m3_res = client.post("/api/v1/ai-fit/color-palette", json={
        "hex_color": "#D2A080"
    })
    assert m3_res.status_code == 200
    col_data = m3_res.json()
    assert col_data["seasonal_tone"] in ["Spring", "Summer", "Autumn", "Winter"]
    assert len(col_data["best_colors"]) >= 4


def test_10_ai_chatbot_rag_and_tracking():
    """Service 7: AI Chatbot answers with RAG citations and tracks live orders."""
    # Store policy question
    q1_res = client.post("/api/v1/chatbot/query", json={
        "query": "What is your policy for exchanges and returns?"
    })
    assert q1_res.status_code == 200
    data1 = q1_res.json()
    assert len(data1["citations"]) > 0

    # Live order inquiry
    q2_res = client.post("/api/v1/chatbot/query", json={
        "query": "Where is my order ORD-SNITCH-88219?"
    })
    assert q2_res.status_code == 200
    data2 = q2_res.json()
    assert data2["order_context"] is not None
    assert "ORD-SNITCH-88219" in data2["order_context"]["order_number"]
