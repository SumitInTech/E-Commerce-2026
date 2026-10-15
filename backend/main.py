"""
========================================================================================
SNITCH LUXE AI E-COMMERCE PLATFORM - MASTER MICROSERVICES ORCHESTRATOR
========================================================================================
Author: Senior Principal ML Systems Architect & Enterprise Designer
Module: backend.main
Description:
    Master entry point exposing the high-throughput API Gateway which orchestrates
    all 7 autonomous platform microservices:
    1. api_gateway/ (Traffic throttling, request tracing, attack sanitization)
    2. auth/ (Buyer, Seller, and Admin JWT workflows with RBAC)
    3. payment/ (Idempotent financial processing, gateway simulation, audit trails)
    4. catalog/ (Product inventory, multi-point anatomical size charts)
    5. order/ (Atomic checkouts, cart management, and 7-stage order tracking)
    6. customer_admin/ (Support ticketing, vendor onboarding, and executive analytics)
    7. ai_fit/ (Direct bridge to ai_models.main_model: Anthropometry & Kinematic Ease)
    8. chatbot/ (Direct bridge to ai_models.main_model: RAG Policy & Live Order Status)

Usage:
    uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
========================================================================================
"""
import sys
import os

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.api_gateway.main import app

# Export app for ASGI webservers
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    from backend.config import settings
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.PORT_GATEWAY, reload=True)
