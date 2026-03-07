from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import activities, auth, dashboard, earnings, expenses

app = FastAPI(title="TVDE Earnings Tracker", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(activities.router, prefix="/api/activities", tags=["activities"])
app.include_router(earnings.router, prefix="/api/earnings", tags=["earnings"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
