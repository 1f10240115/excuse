from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数を読み込み
load_dotenv()

app = FastAPI(
    title="Excuse API Debug",
    description="ExcuseアプリケーションのバックエンドAPI（デバッグ版）",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabaseクライアントの初期化
try:
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_KEY')
    logger.info(f"Supabase URL: {url}")
    logger.info(f"Supabase Key: {key[:20]}..." if key else "None")
    
    # 修正: 正しい方法でクライアントを作成
    supabase = create_client(url, key)
    logger.info("✅ Supabaseクライアント作成成功")
except Exception as e:
    logger.error(f"❌ Supabaseクライアント作成失敗: {e}")
    supabase = None

# データモデル
class ExcuseBase(BaseModel):
    title: str
    description: str
    category: str

class ExcuseCreate(ExcuseBase):
    pass

class Excuse(ExcuseBase):
    id: int
    
    class Config:
        from_attributes = True

# APIエンドポイント
@app.get("/")
async def root():
    logger.info("ルートエンドポイントにアクセス")
    return {"message": "Excuse API Debugへようこそ！"}

@app.get("/health")
async def health_check():
    logger.info("ヘルスチェックエンドポイントにアクセス")
    return {"status": "healthy", "supabase_connected": supabase is not None}

@app.get("/api/excuses", response_model=List[Excuse])
async def get_excuses():
    """全ての言い訳を取得"""
    logger.info("言い訳一覧取得リクエスト")
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabaseクライアントが初期化されていません")
        
        response = supabase.table('excuses').select('*').execute()
        logger.info(f"取得したデータ数: {len(response.data)}")
        return response.data
    except Exception as e:
        logger.error(f"言い訳取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/excuses", response_model=Excuse)
async def create_excuse(excuse: ExcuseCreate):
    """新しい言い訳を作成"""
    logger.info(f"言い訳作成リクエスト: {excuse.title}")
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabaseクライアントが初期化されていません")
        
        # データを準備
        data = {
            'title': excuse.title,
            'description': excuse.description,
            'category': excuse.category
        }
        logger.info(f"挿入するデータ: {data}")
        
        # Supabaseに挿入
        response = supabase.table('excuses').insert(data).execute()
        logger.info(f"挿入結果: {response.data}")
        
        if response.data:
            logger.info(f"✅ 言い訳作成成功: ID {response.data[0]['id']}")
            return response.data[0]
        else:
            logger.error("❌ 挿入結果が空")
            raise HTTPException(status_code=500, detail="データの挿入に失敗しました")
            
    except Exception as e:
        logger.error(f"言い訳作成エラー: {e}")
        import traceback
        logger.error(f"詳細エラー: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    """利用可能なカテゴリを取得"""
    logger.info("カテゴリ一覧取得リクエスト")
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabaseクライアントが初期化されていません")
        
        response = supabase.table('excuses').select('category').execute()
        categories = list(set(item['category'] for item in response.data))
        logger.info(f"取得したカテゴリ: {categories}")
        return {"categories": categories}
    except Exception as e:
        logger.error(f"カテゴリ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info") 