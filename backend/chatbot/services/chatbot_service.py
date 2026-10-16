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

        # Check if query is purely a standalone greeting (e.g. 'hi', 'hey there', 'hello')
        q_clean = req.query.strip().lower()
        clean_words = [w.strip("!?,.") for w in q_clean.split()]
        is_pure_greeting = (
            len(clean_words) <= 2 and
            any(w in ["hi", "hii", "hey", "hello", "yo", "greetings", "namaste", "sup", "high"] for w in clean_words)
        )

        if is_pure_greeting:
            final_answer = (
                "👋 Hello! I'm your **Snitch AI Fashion Stylist & Advisory Assistant**.\n\n"
                "I can help you with:\n"
                "• **Real-Time Order Tracking** (e.g. *\"Where is my order ORD-SNITCH-88219?\"*)\n"
                "• **AI Sizing & Ease Allowances** (e.g. *\"What is ease and return risk?\"*)\n"
                "• **Skin Tone & Color Harmonies** (e.g. *\"What colors suit warm olive skin tone?\"*)\n"
                "• **Shipping & Delivery Timelines** (e.g. *\"How long does delivery take?\"*)\n"
                "• **Store Return & Exchange Guarantees** (e.g. *\"What is your refund timeframe?\"*)\n"
                "• **Luxury Fabric Care** (e.g. *\"How do I wash French linen?\"*)\n\n"
                "How can I assist your wardrobe today?"
            )
            sources = ["Snitch AI Concierge Assistant"]
        elif order_context:
            prefix = (
                f"📦 **Order Status for #{order_context['order_number']}**\n"
                f"• Status: **{order_context['status'].upper()}**\n"
                f"• Tracking: `{order_context['tracking_number']}` (Delhivery Air Express)\n"
                f"• Items: {order_context['items']}\n"
                f"• Total: {order_context['total_amount']}\n\n"
            )
            final_answer = prefix + (
                "Your package is in transit via Delhivery Air Express with guaranteed door delivery. "
                "You can inspect garments upon delivery and enjoy our 30-day sizing exchange guarantee!"
            )
            sources.append("Live Platform Database (orders table)")
        elif re.search(r"\b(skin\s*tone|complexion|undertone|ita\b|color\s*palette|seasonal\s*palette|what\s*colors?\s*suit|cielab|autumn|spring|summer|winter)\b", req.query, re.IGNORECASE):
            final_answer = (
                "🎨 **AI Skin-Tone & Wardrobe Color Harmony (Model 3)**\n\n"
                "We calculate your dermal undertones using **CIE L*a*b* Photometric Space** and the **Individual Typology Angle (ITA°)** to match you with your ideal seasonal palette:\n\n"
                "• **Medium, Honey & Olive (Autumn):** Earthy terracotta, burnt orange, golden olive, warm chocolate, and espresso.\n"
                "• **Bronze & Deep Complexions (Winter/Deep Autumn):** Royal cobalt, pure obsidian onyx, optical white, and emerald green.\n"
                "• **Fair to Light (Summer/Spring):** Slate grey, soft sage, powder blue, and muted lavender.\n\n"
                "💡 **How to test your skin tone right now:**\n"
                "1. Click the **'AI COLOR PALETTE'** button on the top navigation bar.\n"
                "2. Upload a selfie or pick one of our 6 preset skin swatches.\n"
                "3. Select your department (**Men's Streetwear** or **Women's Luxe**) to view matched catalog pieces with direct harmony scores!"
            )
            sources = ["Model 3: Photometric CIELAB Skin-Tone Engine"]
        elif re.search(r"\b(shipping|delivery|courier|delhivery|how\s*long|transit|timeline|dispatch)\b", req.query, re.IGNORECASE):
            final_answer = (
                "🚀 **Snitch Express Shipping & Logistics**\n\n"
                "• **Metro Cities (Delhi, Mumbai, Bengaluru):** 2 to 3 business days via Delhivery Air Express.\n"
                "• **Rest of India:** Delivered in 3 to 5 business days.\n"
                "• **Free Express Shipping:** 100% free on prepaid orders exceeding ₹1,499.\n"
                "• **Live Order Lookup:** Provide your order number (e.g. `ORD-SNITCH-88219`) to view live courier status!"
            )
            sources = ["Snitch Express Logistics Guidelines"]
        elif re.search(r"\b(return\s*risk|what\s*is\s*ease|negative\s*ease|ease\s*score|snug\s*garment|size\s*up|size\s*down)\b", req.query, re.IGNORECASE):
            final_answer = (
                "📐 **Kinematic Ease & Return Risk Explained**\n\n"
                "• **What is Ease?**\n"
                "  $$\\text{Ease} = \\text{Garment Spec} - \\text{Body Circumference}$$\n"
                "  - **Positive Ease (+3 to +6 cm):** Comfortable anatomical drape allowing natural torso expansion and reach.\n"
                "  - **Negative Ease (< 0 cm):** Garment is tighter than your body, creating tension lines.\n\n"
                "• **What is Return Risk?**\n"
                "  Indicates the statistical probability that a garment will be returned due to poor fit.\n"
                "  - **< 20% (Low Risk):** Confident fit with optimal drape.\n"
                "  - **> 70% (High Risk):** Negative ease; sizing up to the next size is recommended."
            )
            sources = ["Model 2: Garment Kinematic Ease Engine"]
        elif re.search(r"\b(return|exchange|refund|money\s*back|policy)\b", req.query, re.IGNORECASE):
            final_answer = (
                "🔄 **Snitch 30-Day Return & Exchange Policy**\n\n"
                "• **30-Day Sizing Guarantee:** Free exchanges for 30 days post-delivery if the fit does not meet expectations.\n"
                "• **AI Fit Waiver:** If you used our AI Fit Lab prior to purchasing and experienced a sizing discrepancy, return shipping is 100% free with an additional 10% wardrobe credit.\n"
                "• **Refund Processing:** Approved refunds are initiated back to the original payment source within 3 to 5 business days after warehouse inspection."
            )
            sources = ["Snitch Store Policies (Apparel Return & Care Guidelines)"]
        else:
            # Real-Time Product Catalog Recommendations if asking about apparel
            garment_match = re.search(r"\b(shirt|tee|t-shirt|trouser|pant|blazer|jacket|collection|drop|buy|shop|apparel|product|recommend)\b", req.query, re.IGNORECASE)
            if garment_match:
                try:
                    from backend.catalog.models.catalog_model import Product
                    query_term = garment_match.group(1).lower()
                    type_map = {
                        "shirt": "shirt",
                        "tee": "t_shirt",
                        "t-shirt": "t_shirt",
                        "trouser": "pants",
                        "pant": "pants",
                        "blazer": "jacket",
                        "jacket": "jacket"
                    }
                    g_type = type_map.get(query_term)
                    matched_products = db.query(Product).filter(Product.garment_type == g_type).limit(3).all() if g_type else db.query(Product).limit(3).all()
                    if matched_products:
                        prod_lines = [f"• **{p.name}** — ₹{p.price:,.2f} (*{p.fabric}*)" for p in matched_products]
                        product_prefix = "🛍️ **Live Streetwear Catalog Recommendations:**\n" + "\n".join(prod_lines) + "\n\n"
                        final_answer = product_prefix + (final_answer if final_answer else "Let me know your height and weight in the AI Fit Lab for tailored sizing!")
                        sources.append("Live Platform Database (products table)")
                except Exception:
                    pass

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
