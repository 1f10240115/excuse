from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.get("/check-env")
async def check_env():
    """環境変数チェック - ログ付き"""
    logger.info("環境変数チェック開始")
    
    # すべての環境変数をログに出力
    all_env = dict(os.environ)
    logger.info(f"環境変数の数: {len(all_env)}")
    
    # Supabase関連の環境変数を確認
    supabase_vars = {}
    for key, value in all_env.items():
        if "SUPABASE" in key.upper():
            supabase_vars[key] = value[:10] + "..." if len(value) > 10 else value
            logger.info(f"Found Supabase var: {key}")
    
    logger.info(f"Supabase変数の数: {len(supabase_vars)}")
    
    return {
        "total_env_vars": len(all_env),
        "supabase_vars": supabase_vars,
        "status": "checked"
    }

@app.get("/basic")
async def basic():
    """基本的なテスト - 環境変数なし"""
    return {
        "message": "Basic endpoint works",
        "timestamp": "2024-01-01",
        "status": "ok"
    }

@app.get("/os-test")
async def os_test():
    """OS情報テスト - 環境変数なし"""
    return {
        "platform": os.name,
        "cwd": os.getcwd(),
        "status": "os_info"
    } 