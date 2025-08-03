from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate_excuse")
async def generate_excuse(request: Request):
    """シンプルな言い訳生成"""
    try:
        # リクエストデータを取得
        data = await request.json()
        minutes = data.get("minutes", "")
        cause = data.get("cause", "")
        target = data.get("target", "")
        detail = data.get("detail", "")
        
        # シンプルな言い訳を生成
        generated_excuse = f"申し訳ございません。{minutes}分{cause}のため、{target}に遅刻いたします。{detail}"
        
        return {
            "title": "シンプル生成言い訳",
            "description": generated_excuse,
            "category": "シンプル"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "title": "エラー",
            "description": "言い訳の生成に失敗しました",
            "category": "エラー"
        }

@app.get("/")
async def root():
    return {"message": "シンプルAPI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 