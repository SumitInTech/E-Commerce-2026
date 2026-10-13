"""
FastAPI Application Entry Point.
Combines all 4 Machine Learning and AI models into a unified, high-performance API.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.exceptions import AnthropometricException, map_domain_exception_to_http
from app.routers import health, fit_check, recommend, color, chatbot

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production AI/ML Microservice providing: \n"
        "1. Model 1: Body Measurement Regressor (Dual-view 2D silhouettes -> 3D circumferences)\n"
        "2. Model 2: Size Fit Recommender (Kinematic ease & return-minimization sizing)\n"
        "3. Model 3: Photometric CIELAB Skin-Tone & Seasonal Color Matcher\n"
        "4. Model 4: Knowledge-Grounded RAG Stylist & Support Chatbot"
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(AnthropometricException)
async def anthropometric_exception_handler(request: Request, exc: AnthropometricException):
    http_exc = map_domain_exception_to_http(exc)
    return JSONResponse(status_code=http_exc.status_code, content=http_exc.detail)


# Register Routers
app.include_router(health.router)
app.include_router(fit_check.router)
app.include_router(recommend.router)
app.include_router(color.router)
app.include_router(chatbot.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
