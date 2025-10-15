from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ Import routes and modules
from app import jwt_auth
from app.routes import contacts, campaigns, calls, call_history
from app.models.db import init_db
from app.routes import contact_crud
from app.routes import campaign_crud
from app.routes import calls
from app.routes import knowledge_base
from app.routes import analytics
from app.routes import websocket_progress

# ✅ Initialize FastAPI app FIRST
app = FastAPI(
    title="AI Calling Agent Backend",
    version="1.0.0",
    description="Backend service for AI-powered calling platform (MVP Phase 1)",
)

# ✅ Event hook to initialize DB
@app.on_event("startup")
def on_startup():
    init_db()

# ✅ Enable CORS for frontend/local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register API routers
app.include_router(jwt_auth.router, prefix="/v1", tags=["Auth"])
app.include_router(contacts.router, prefix="/v1/contacts", tags=["Contacts"])
app.include_router(campaigns.router, prefix="/v1/campaigns", tags=["Campaigns"])
app.include_router(campaigns.router, prefix="/v1/schedule-campaign", tags=["Schedule Campaign"])
app.include_router(calls.router, prefix="/v1/calls", tags=["Calls"])
app.include_router(call_history.router, prefix="/v1/calls", tags=["Call History"])
app.include_router(contact_crud.router, prefix="/v1/contacts", tags=["Contacts DB"])
app.include_router(campaign_crud.router, prefix="/v1/campaigns/db", tags=["Campaign DB"])
app.include_router(knowledge_base.router, prefix="/v1/knowledge", tags=["Knowledge Base"])
app.include_router(analytics.router, prefix="/v1/analytics", tags=["Analytics"])
app.include_router(websocket_progress.router)

# ✅ Health check route
@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Calling Agent Backend is running."}
