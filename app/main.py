"""
TermScan API - Main Application Entry Point

An AI-powered API that analyzes contracts for compliance (Islamic, ESG, Legal, and more).
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
import os

from app.core.config import settings
from app.api.v1 import contracts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"\n🔍 {settings.app_name} starting...")
    print(f"📍 Environment: {settings.app_env}")
    print(f"🤖 AI Provider: {settings.ai_provider}")
    print(f"📚 API Docs: http://{settings.host}:{settings.port}/docs\n")
    
    yield
    
    # Shutdown
    print(f"\n👋 {settings.app_name} shutting down...\n")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="""
## TermScan - AI Contract Compliance API

Analyze contracts for compliance with multiple frameworks: Islamic (Shariah), ESG, Legal, and more.

### Features

- **Full Analysis**: Detailed compliance report with scores, flags, and recommendations
- **Quick Score**: Fast compliance scoring for initial screening
- **Multiple Contract Types**: Employment, service, sale, lease, partnership, and more
- **Scholarly References**: Citations from Quran, Hadith, and Islamic jurisprudence

### Principles Checked

| Principle | Arabic | Description |
|-----------|--------|-------------|
| Riba | ربا | Interest/usury |
| Gharar | غرر | Excessive uncertainty |
| Maysir | ميسر | Gambling/speculation |
| Haram Industries | حرام | Forbidden sectors |
| Dhulm | ظلم | Oppression/unfair terms |
| Tadlis | تدليس | Deception/hidden clauses |

### Authentication

All endpoints require an API key in the Authorization header:

```
Authorization: Bearer your_api_key_here
```

### Rate Limits

| Tier | Requests/Month | Rate/Minute |
|------|----------------|-------------|
| Free | 50 | 10 |
| Starter | 500 | 30 |
| Growth | 5,000 | 100 |
| Enterprise | Unlimited | 500 |
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 3))
    return response


# Include routers
app.include_router(
    contracts.router,
    prefix="/v1",
)


# Serve the web UI
@app.get("/", tags=["UI"])
async def serve_ui():
    """Serve the web interface"""
    static_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(static_path)


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "environment": settings.app_env,
        "ai_provider": settings.ai_provider,
        "ai_model": settings.ai_model,
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
            "code": "INTERNAL_ERROR",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
