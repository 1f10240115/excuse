from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API は動作しています!"}

@app.get("/env")
async def env():
    """環境変数テスト"""
    return {
        "supabase_url": os.environ.get("SUPABASE_URL", "NOT_SET"),
        "supabase_key": os.environ.get("SUPABASE_KEY", "NOT_SET")[:10] + "..." if os.environ.get("SUPABASE_KEY") else "NOT_SET",
        "supabase_service_key": os.environ.get("SUPABASE_SERVICE_KEY", "NOT_SET")[:10] + "..." if os.environ.get("SUPABASE_SERVICE_KEY") else "NOT_SET",
        "debug": os.environ.get("DEBUG", "NOT_SET")
    } 