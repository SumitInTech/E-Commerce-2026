"""
Autonomous AI Chatbot Microservice Application.
Can be executed as an independent container/process on port 8007.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.chatbot.routers.chatbot_router import router as chatbot_router
from backend.database.supabase_client import init_db

app = FastAPI(
    title=f"{settings.PROJECT_NAME} - AI Chatbot Microservice",
    version=settings.VERSION,
    description="Dedicated microservice delivering real-time policy and order responses grounded in platform data."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"service": "ai_chatbot_service", "status": "HEALTHY", "port": settings.PORT_CHATBOT}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.chatbot.main:app", host="0.0.0.0", port=settings.PORT_CHATBOT, reload=True)
