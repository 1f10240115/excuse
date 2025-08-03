# backend/gemini_client.py
import os, time, random
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from google import genai
from google.genai import types

MODEL_ID = "gemini-1.5-flash"

class TransientAIError(Exception):
    """503 など一時的な障害を表す例外"""

class GeminiClient:
    def __init__(self, api_key: str | None = None):
        key = api_key or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError("GOOGLE_API_KEY が設定されていません（backend/.env）")
        self.client = genai.Client(api_key=key)

    def _call_once(self, system: str, user: str) -> str:
        resp = self.client.models.generate_content(
            model=MODEL_ID,
            contents=[system, user],
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=60,
            ),
        )
        return (getattr(resp, "text", "") or "").strip()

    def generate_excuse(self, minutes: str, cause: str, target: str, detail: str) -> str:
        # 時間の表記
        if minutes == "60":
            time_jp = "一時間"
        elif minutes:
            time_jp = f"{minutes}分"
        else:
            time_jp = "未選択"


        polite_targets = ("上司", "同僚", "先輩", "先生(教授)", "バイト先")
        casual_targets = ("友達", "家族")
        tone = "丁寧" if target in polite_targets else ("カジュアル" if target in casual_targets else "ニュートラル")

        system = (
          "あなたは日本語で、LINE/SMS向けの短い遅刻連絡文を書くアシスタントです。"
          "出力は1〜3文、絵文字や顔文字は使わないでください。追加説明に文章の長さが指定されていた場合、5文まで可能です。"
          "minutes_selected が false であり、追加説明に時間表現がない場合、数値の時間表現（例: 3分, 10分, 一時間 など）を絶対に出力してはいけません。"
          "その場合は『少し』『少々』『まもなく』などの非数値の表現のみを使ってください。"
          "minutes_selected が true のときは minutes_label の値（例: 3分/5分/…/一時間）をそのまま使い、変更しないでください。"
          "対象に応じて文体を切り替えてください：上司/同僚/先輩→丁寧、友達/家族→カジュアル。"
          "原因と追加説明に別の内容が書かれていた場合、その両方の内容を文章に含めてください。"
        )

        user = (
            f"到着まで:{time_jp} / 原因:{cause or '未選択'} / 相手:{target or '未選択'} / 追加説明:{detail or 'なし'}\n"
            f"文体:{tone}。自然な日本語で1~3文程度の言い訳を書いてください。"
        )

        # 503 などの一時エラーは指数バックオフで最大4回まで再試行
        attempts = 4
        for i in range(attempts):
            try:
                text = self._call_once(system, user)
                if not text:
                    # 応答が空なら恒久的エラーとして扱う
                    raise RuntimeError("空の応答")
                return text
            except Exception as e:
                msg = str(e)
                # エラーメッセージ内の 503/UNAVAILABLE/overloaded を簡易判定
                transient = ("503" in msg) or ("UNAVAILABLE" in msg.upper()) or ("overloaded" in msg.lower())
                if transient and i < attempts - 1:
                    # 指数バックオフ＋ジッター（0.3〜）
                    wait = (2 ** i) + random.uniform(0.3, 0.9)
                    time.sleep(wait)
                    continue
                if transient:
                    raise TransientAIError(msg)
                raise  # 恒久的エラーは即時伝播