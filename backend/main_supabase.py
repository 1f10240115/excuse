from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
from supabase import create_client
import os

# Supabaseクライアントの初期化
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase = create_client(url, key)

app = FastAPI(
    title="Excuse API",
    description="ExcuseアプリケーションのバックエンドAPI",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000", 
        "http://127.0.0.1:8000",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"message": "Excuse APIへようこそ！"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/excuses", response_model=List[Excuse])
async def get_excuses():
    """全ての言い訳を取得"""
    try:
        response = supabase.table('excuses').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/excuses/{excuse_id}", response_model=Excuse)
async def get_excuse(excuse_id: int):
    """指定されたIDの言い訳を取得"""
    try:
        response = supabase.table('excuses').select('*').eq('id', excuse_id).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="言い訳が見つかりません")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/excuses", response_model=Excuse)
async def create_excuse(excuse: ExcuseCreate):
    """新しい言い訳を作成"""
    try:
        response = supabase.table('excuses').insert({
            'title': excuse.title,
            'description': excuse.description,
            'category': excuse.category
        }).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    """利用可能なカテゴリを取得"""
    try:
        response = supabase.table('excuses').select('category').execute()
        categories = list(set(item['category'] for item in response.data))
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
