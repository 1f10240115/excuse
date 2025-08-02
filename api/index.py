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

@app.get("/env-debug")
async def env_debug():
    """環境変数の詳細デバッグ"""
    all_env_vars = dict(os.environ)
    
    # Supabase関連の環境変数を抽出
    supabase_vars = {}
    for key, value in all_env_vars.items():
        if "SUPABASE" in key.upper():
            # セキュリティのため、キーの一部のみ表示
            if len(value) > 10:
                supabase_vars[key] = value[:10] + "..."
            else:
                supabase_vars[key] = value
    
    return {
        "all_environment_variables_count": len(all_env_vars),
        "supabase_variables": supabase_vars,
        "available_keys": list(all_env_vars.keys())[:10],  # 最初の10個のキーを表示
        "python_path": os.environ.get("PYTHONPATH", "NOT_SET"),
        "vercel_env": os.environ.get("VERCEL_ENV", "NOT_SET")
    } 