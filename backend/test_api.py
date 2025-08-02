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

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/test")
async def test():
    return {"test": "success"}

@app.get("/info")
async def info():
    return {
        "name": "Excuse API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/env-test")
async def env_test():
    """環境変数のテスト"""
    env_vars = {
        "SUPABASE_URL": os.environ.get("SUPABASE_URL", "NOT_SET"),
        "SUPABASE_KEY": os.environ.get("SUPABASE_KEY", "NOT_SET"),
        "SUPABASE_SERVICE_KEY": os.environ.get("SUPABASE_SERVICE_KEY", "NOT_SET"),
        "DEBUG": os.environ.get("DEBUG", "NOT_SET"),
    }
    
    # セキュリティのため、キーの一部のみ表示
    for key in ["SUPABASE_KEY", "SUPABASE_SERVICE_KEY"]:
        if env_vars[key] != "NOT_SET" and len(env_vars[key]) > 10:
            env_vars[key] = env_vars[key][:10] + "..."
    
    return {
        "environment_variables": env_vars,
        "status": "environment_check"
    } 