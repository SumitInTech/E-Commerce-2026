"""
AI Chatbot Service.
Delivers real-time customer support grounded in store policy, sizing guidelines,
and live database records (Order Tracking & Catalog availability).
"""
import re
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from ai_models.main_model import get_ai_hub
from backend.models import Order
from backend.schemas.chatbot import ChatbotQueryRequest, ChatbotQueryResponse, CitationItem


class AIChatbotService:
    @staticmethod
    async def answer_query(db: Session, req: ChatbotQueryRequest) -> ChatbotQueryResponse:
        hub = get_ai_hub()
        query = req.query.strip()
        order_context = None

        # 1. Check if user provided or query mentions an order number
        order_match = re.search(r"(ORD-[A-Z0-9\-]+)", query, re.IGNORECASE)
        order_num = req.order_number or (order_match.group(1).upper() if order_match else None)

        if order_num:
            order = db.query(Order).filter(Order.order_number == order_num).first()
            if order:
                items_desc = ", ".join([f"{it.product_name} ({it.size_label})" for it in order.items])
                order_context = {
                    "order_number": order.order_number,
                    "status": order.status.value,
                    "customer_name": order.customer_name,
                    "tracking_number": order.tracking_number,
                    "total_amount": f"₹{order.total_amount:,.2f}",
                    "items": items_desc
                }
                # Prepend live order context to query for RAG
                augmented_query = (
                    f"Customer is asking about Order {order.order_number}. "
                    f"Current status: {order.status.value.upper()}, Tracking: {order.tracking_number}, "
                    f"Items: {items_desc}. Query: {query}"
                )
            else:
                augmented_query = f"Customer queried order {order_num}, but it was not found in the database. Query: {query}"
        else:
            augmented_query = query

        # 2. Query Unified AI Hub RAG engine
        res = await hub.answer_chatbot_query(augmented_query, top_k=req.top_k)

        # If order context was found, synthesize clear tracking response
        response_text = res["response"]
        if order_context:
            prefix = (
                f"📦 **Order Status for #{order_context['order_number']}**\n"
                f"• Status: **{order_context['status'].upper()}**\n"
                f"• Tracking: `{order_context['tracking_number']}` (Delhivery Air Express)\n"
                f"• Items: {order_context['items']}\n"
                f"• Total: {order_context['total_amount']}\n\n"
            )
            response_text = prefix + response_text

        citations_list = [
            CitationItem(
                id=c["id"],
                topic=c.get("topic"),
                source=c.get("source"),
                relevance_score=c.get("relevance_score")
            )
            for c in res.get("citations", [])
        ]

        return ChatbotQueryResponse(
            status="success",
            query=query,
            response=response_text,
            order_context=order_context,
            citations=citations_list
        )
