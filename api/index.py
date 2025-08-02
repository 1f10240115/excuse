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

@app.get("/test")
async def test():
    return {"test": "success"}

@app.get("/simple-env")
async def simple_env():
    """シンプルな環境変数テスト"""
    return {
        "supabase_url": os.environ.get("SUPABASE_URL", "NOT_SET"),
        "status": "simple_test"
    }

@app.get("/env")
async def env():
    """環境変数テスト - 安全版"""
    try:
        supabase_url = os.environ.get("SUPABASE_URL", "NOT_SET")
        supabase_key = os.environ.get("SUPABASE_KEY", "NOT_SET")
        supabase_service_key = os.environ.get("SUPABASE_SERVICE_KEY", "NOT_SET")
        debug = os.environ.get("DEBUG", "NOT_SET")
        
        # セキュリティのため、キーの一部のみ表示
        if supabase_key != "NOT_SET" and len(supabase_key) > 10:
            supabase_key = supabase_key[:10] + "..."
        
        if supabase_service_key != "NOT_SET" and len(supabase_service_key) > 10:
            supabase_service_key = supabase_service_key[:10] + "..."
        
        return {
            "supabase_url": supabase_url,
            "supabase_key": supabase_key,
            "supabase_service_key": supabase_service_key,
            "debug": debug,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        } 