from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
from supabase import create_client
import os
from dotenv import load_dotenv
from fastapi import Request

# 環境変数を読み込み
load_dotenv()

# Supabaseクライアントの初期化
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Warning: Supabase環境変数が設定されていません")
    print(f"SUPABASE_URL: {url}")
    print(f"SUPABASE_SERVICE_KEY: {key[:10] + '...' if key else 'None'}")

supabase = create_client(url, key) if url and key else None

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
    user_id: str

class Excuse(ExcuseBase):
    id: int
    user_id: str
    
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
async def get_excuses(user_id: str = None):
    """ユーザーの言い訳を取得"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabaseクライアントが初期化されていません")
    try:
        if user_id:
            # 特定のユーザーの言い訳のみ取得
            response = supabase.table('excuses').select('*').eq('user_id', user_id).execute()
        else:
            # 全ての言い訳を取得（管理者用）
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
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabaseクライアントが初期化されていません")
    try:
        response = supabase.table('excuses').insert({
            'title': excuse.title,
            'description': excuse.description,
            'category': excuse.category,
            'user_id': excuse.user_id
        }).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_excuse")
async def generate_excuse(request: Request):
    """Gemini APIを使用して言い訳を生成"""
    try:
        # リクエストデータを取得
        data = await request.json()
        minutes = data.get("minutes", "")
        cause = data.get("cause", "")
        target = data.get("target", "")
        detail = data.get("detail", "")
        
        # デバッグ用：受信したデータをログ出力
        print(f"Received data: minutes={minutes}, cause={cause}, target={target}, detail={detail}")
        
        # Gemini APIを使用して言い訳を生成
        try:
            import google.generativeai as genai
            
            # 環境変数からAPIキーを取得
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                # APIキーがない場合はサンプルデータを返す
                return {
                    "title": "生成された言い訳",
                    "description": f"{minutes}分{cause}で{target}への言い訳: {detail}",
                    "category": "その他"
                }
            
            # Gemini APIを設定
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # プロンプトを作成
            prompt = f"""
            以下の条件で言い訳を生成してください：
            
            遅延時間: {minutes}分
            原因: {cause}
            対象者: {target}
            詳細: {detail}
            
            自然で信頼できる言い訳を日本語で生成してください。
            """
            
            # 言い訳を生成
            response = model.generate_content(prompt)
            generated_excuse = response.text
            
            return {
                "title": "AI生成言い訳",
                "description": generated_excuse,
                "category": "AI生成"
            }
        except ImportError:
            # google-generativeaiがインストールされていない場合
            return {
                "title": "生成された言い訳",
                "description": f"{minutes}分{cause}で{target}への言い訳: {detail}",
                "category": "その他"
            }
        
    except Exception as e:
        print(f"Error in generate_excuse: {str(e)}")
        # エラーが発生した場合はサンプルデータを返す
        return {
            "title": "エラー時の言い訳",
            "description": f"申し訳ございません。{minutes}分{cause}のため、{target}に遅刻いたします。{detail}",
            "category": "エラー"
        }

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
