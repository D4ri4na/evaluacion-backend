from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import get_db_connection
from routers.v1.events import router as events_router

app = FastAPI(
    title="Tickets API",
    openapi_url="/openapi.json",
    root_path="/api" 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router, prefix="/v1")

@app.get("/v1/healthz")
def health_check():
    db_conn = get_db_connection()
    if db_conn:
        db_conn.close()
        return {"status": "ok"}
    raise HTTPException(status_code=503, detail="Database unhealthy")