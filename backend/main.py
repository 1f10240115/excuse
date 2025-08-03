from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from gemini_client import GeminiClient, TransientAIError


from dotenv import load_dotenv; load_dotenv()
import os
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


app = FastAPI(
    title="Excuse API",
    description="ExcuseアプリケーションのバックエンドAPI",
    version="1.0.0"
)

class ExcuseReq(BaseModel):
    minutes: str  # "" | "3" | "5" | "10" | "15" | "30" | "60"
    cause: str    # "寝坊" 等 or ""
    target: str   # "上司" 等 or ""
    detail: str   # テキストボックス

class ExcuseRes(BaseModel):
    excuse: str

gemini = GeminiClient()

@app.post("/generate_excuse", response_model=ExcuseRes)
def generate_excuse(req: ExcuseReq):
    try:
        text = gemini.generate_excuse(req.minutes, req.cause, req.target, req.detail)
        return {"excuse": text}
    except TransientAIError as e:
        # モデル過負荷などの一時エラーは 503
        raise HTTPException(
            status_code=503,
            detail="AIが混雑しています。しばらくしてからもう一度お試しください。"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")



# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データモデル
class ExcuseBase(BaseModel):
    # title: str
    description: str
    # category: str

class ExcuseCreate(ExcuseBase):
    pass

class Excuse(ExcuseBase):
    id: int
    
    class Config:
        from_attributes = True

# サンプルデータ
excuses_db = [
    {
        "id": 1,
        # "title": "電車が遅延",
        "description": "電車が遅延してしまいました",
        # "category": "交通"
    },
    {
        "id": 2,
        # "title": "体調不良",
        "description": "体調が悪くて出社できませんでした",
        # "category": "健康"
    },
    {
        "id": 3,
        # "title": "家族の急用",
        "description": "家族に急用ができて対応していました",
        # "category": "家族"
    }
]

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
    return excuses_db

@app.get("/api/excuses/{excuse_id}", response_model=Excuse)
async def get_excuse(excuse_id: int):
    """指定されたIDの言い訳を取得"""
    for excuse in excuses_db:
        if excuse["id"] == excuse_id:
            return excuse
    raise HTTPException(status_code=404, detail="言い訳が見つかりません")

@app.post("/api/excuses", response_model=Excuse)
async def create_excuse(excuse: ExcuseCreate):
    """新しい言い訳を作成"""
    new_id = max(excuse["id"] for excuse in excuses_db) + 1 if excuses_db else 1
    new_excuse = {
        "id": new_id,
        # "title": excuse.title,
        "description": excuse.description,
        # "category": excuse.category
    }
    excuses_db.append(new_excuse)
    return new_excuse

@app.get("/api/categories")
async def get_categories():
    """利用可能なカテゴリを取得"""
    categories = list(set(excuse["category"] for excuse in excuses_db))
    return {"categories": categories}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 