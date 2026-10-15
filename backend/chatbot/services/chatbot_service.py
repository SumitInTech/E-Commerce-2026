"""
AI Chatbot Business Domain Service.
Integrates Model 4 (RAG store policy semantic retrieval) with live database order tracking.
"""
import uuid
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from ai_models.main_model import get_ai_hub
from backend.chatbot.models.chatbot_model import ChatSession, ChatMessage
from backend.chatbot.schemas.chatbot_schema import ChatQueryRequest, CitationItem
from backend.order.models.order_model import Order


class ChatbotService:
    def __init__(self):
        self._hub = None

    @property
    def hub(self):
        if self._hub is None:
            self._hub = get_ai_hub()
        return self._hub

    async def answer_query(self, db: Session, req: ChatQueryRequest) -> Dict[str, Any]:
        session_id = req.session_id or f"sess_{uuid.uuid4().hex[:12]}"

        # Ensure session exists in DB
        chat_sess = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not chat_sess:
            chat_sess = ChatSession(session_id=session_id, user_id=req.user_id)
            db.add(chat_sess)
            db.commit()

        # Save user message
        user_msg = ChatMessage(session_id=session_id, role="user", content=req.query)
        db.add(user_msg)
        db.commit()

        # 1. Order Status Detection: Check if query or order_number field mentions an order
        order_context = None
        order_match = re.search(r"(ORD-[A-Z0-9\-]+)", req.query, re.IGNORECASE)
        num_match = re.search(r'(?:order|track|item|#)\s*#?(\d+)', req.query, re.IGNORECASE)

        order_num = req.order_number or (order_match.group(1).upper() if order_match else None)
        order = None
        if order_num:
            order = db.query(Order).filter(Order.order_number == order_num).first()
        elif num_match:
            order_id = int(num_match.group(1))
            order = db.query(Order).filter(Order.id == order_id).first()

        if order:
            items_desc = ", ".join([f"{it.product_name} ({it.size_label})" for it in order.items]) if order.items else "Apparel garments"
            st_val = order.status.value if hasattr(order.status, "value") else str(order.status)
            order_context = {
                "order_id": order.id,
                "order_number": order.order_number,
                "status": st_val,
                "customer_name": order.customer_name,
                "tracking_number": order.tracking_number,
                "total_amount": f"₹{order.total_amount:,.2f}" if isinstance(order.total_amount, (int, float)) else str(order.total_amount),
                "items": items_desc,
                "shipping_address": order.shipping_address
            }
            augmented_query = (
                f"Customer is asking about Order {order.order_number}. "
                f"Current status: {st_val.upper()}, Tracking: {order.tracking_number}, "
                f"Items: {items_desc}. Query: {req.query}"
            )
        else:
            augmented_query = req.query

        # 2. Invoke RAG service from ai_models.main_model
        ai_response = await self.hub.answer_chatbot_query(augmented_query, top_k=req.top_k)

        final_answer = ai_response.get("response") or ai_response.get("answer", "")
        citations_raw = ai_response.get("citations", [])
        sources = ai_response.get("sources", [])
        if not sources and citations_raw:
            sources = [c.get("source") or c.get("topic") for c in citations_raw if c.get("source") or c.get("topic")]
        if not sources:
            sources = ["Snitch Store Policies (Apparel Return & Care Guidelines)"]

        # If order context was detected, enrich the answer with ground-truth fulfillment data
        if order_context:
            prefix = (
                f"📦 **Order Status for #{order_context['order_number']}**\n"
                f"• Status: **{order_context['status'].upper()}**\n"
                f"• Tracking: `{order_context['tracking_number']}` (Delhivery Air Express)\n"
                f"• Items: {order_context['items']}\n"
                f"• Total: {order_context['total_amount']}\n\n"
            )
            final_answer = prefix + final_answer
            sources.append("Live Platform Database (orders table)")

        # Save assistant message
        bot_msg = ChatMessage(session_id=session_id, role="assistant", content=final_answer)
        db.add(bot_msg)
        db.commit()

        citations_list = [
            CitationItem(
                id=c["id"],
                topic=c.get("topic", "Store Policy"),
                source=c.get("source", "Snitch Care Guidelines"),
                relevance_score=c.get("relevance_score", 0.95)
            )
            for c in citations_raw
        ]
        if not citations_list and sources:
            citations_list = [
                CitationItem(id=idx + 1, topic="Store Policy", source=s, relevance_score=0.95)
                for idx, s in enumerate(sources)
            ]

        return {
            "session_id": session_id,
            "answer": final_answer,
            "response": final_answer,
            "sources": sources,
            "citations": citations_list,
            "order_context": order_context,
            "timestamp": datetime.now(timezone.utc),
            "status": "success",
            "query": req.query
        }

    @staticmethod
    def get_history(db: Session, session_id: str) -> List[ChatMessage]:
        return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.id.asc()).all()


chatbot_service = ChatbotService()
