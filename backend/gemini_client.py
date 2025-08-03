# backend/gemini_client.py
import os
import time
import random
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from google import genai
from google.genai import types

MODEL_ID = "gemini-1.5-flash"


class TransientAIError(Exception):
    """503 など一時的な障害を表す例外"""
    pass


class GeminiClient:
    def __init__(self, api_key: str | None = None):
        key = api_key or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError("GOOGLE_API_KEY が設定されていません（backend/.env か環境変数を確認してください）")
        self.client = genai.Client(api_key=key)

    def _call_once(
        self,
        system: str,
        user: str,
        *,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ) -> str:
        resp = self.client.models.generate_content(
            model=MODEL_ID,
            contents=[system, user],
            config=types.GenerateContentConfig(
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_tokens,
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

        minutes_selected = bool(minutes)
        minutes_label = time_jp if minutes_selected else ""

        polite_targets = ("上司", "同僚", "先輩", "先生(教授)", "バイト先")
        casual_targets = ("友達", "家族")
        tone = "丁寧" if target in polite_targets else ("カジュアル" if target in casual_targets else "ニュートラル")

        # プロンプト切り替えと生成設定
        if cause == "大喜利":
            system = (
                "あなたは日本語で、遅刻連絡を『短く面白く』『突拍子のある要素をさりげなく混ぜた』形で書くコピーライターです。"
                "出力は1〜3文。絵文字・顔文字・メタ語（例: 大喜利、冗談、ネタ等）は使わない。"
                "minutes_selected=false かつ追加説明に時間表現がない場合、数値時間（例: 3分、10分、一時間）は一切出さず、"
                "『少し』『少々』『まもなく』などの曖昧表現のみを使う。追加説明に時間表現がある時はその限りではない。"
                "minutes_selected=true のときは minutes_label をそのまま使い、言い換えをしない。"
                "相手に応じて文体を切り替える（上司/同僚/先輩/先生(教授)/バイト先→丁寧、友達/家族→カジュアル）。"
                "スタイル: ありえないような出来事や誇張、擬人化、想像力の飛んだ設定を１つ含めて、テンポ良く伝える。"
                "以下のような多様な発想源（例：日常の奇妙な出来事、時間のズレ、動物・物の擬人化、歴史や文化の混ざった誤解、テクノロジーの暴走、魔法的事件、名指しの有名人のトラブル、食べ物の事件、天候の異常、タイムトラベルの副作用、偶然のダブルブッキング、自己の分身の誤作動、伝説生物の出現、誤認・勘違いなど）からランダムに一つを選ぶか自分で考え、誰も予想しないけれど「なるほどそれで？」とツッコミたくなるような言い訳を作ってください。"
                "不快・差別的・実害を想起させる災害描写は避ける。"
                "文の中に『大喜利』などの説明的な語は出さず自然に書く。"
            )
            gen_cfg = dict(temperature=0.95, top_p=0.95, max_tokens=100)
        else:
            system = (
                "あなたは日本語で、LINE/SMS向けの短い遅刻連絡文を書くアシスタントです。"
                "出力は1〜3文、絵文字や顔文字は使わない。追加説明に文章の長さ指定がある場合は最大5文まで可。"
                "minutes_selected=false かつ追加説明に時間表現がないとき、数値の時間（例: 3分/10分/一時間）を出さず、"
                "『少し』『少々』『まもなく』などの非数値表現のみを使う。追加説明に時間表現がある時はその限りではない。"
                "minutes_selected=true のときは minutes_label をそのまま使い、言い換えしない。"
                "相手に応じて文体を切り替える（上司/同僚/先輩/先生(教授)/バイト先→丁寧、友達/家族→カジュアル）。"
                "原因と追加説明に異なる内容があれば両方を自然に含める。"
            )
            gen_cfg = dict(temperature=0.70, top_p=0.90, max_tokens=80)

        # user 側は構造化して要件だけ書く
        user = (
            "【入力】\n"
            f"minutes_selected={str(minutes_selected).lower()}\n"
            f"minutes_label={minutes_label}\n"
            f"cause={cause or '未選択'}\n"
            f"target={target or '未選択'}\n"
            f"tone={tone}\n"
            f"detail={detail or 'なし'}\n"
            "【要件】自然な日本語で1〜3文の遅刻連絡文を生成する。余計な注釈やラベルは書かない。"
        )

        attempts = 4
        for i in range(attempts):
            try:
                text = self._call_once(
                    system,
                    user,
                    temperature=gen_cfg["temperature"],
                    top_p=gen_cfg["top_p"],
                    max_tokens=gen_cfg["max_tokens"],
                )
                if not text:
                    raise RuntimeError("空の応答")
                return text
            except Exception as e:
                msg = str(e)
                transient = ("503" in msg) or ("UNAVAILABLE" in msg.upper()) or ("overloaded" in msg.lower())
                if transient and i < attempts - 1:
                    wait = (2 ** i) + random.uniform(0.3, 0.9)
                    time.sleep(wait)
                    continue
                if transient:
                    raise TransientAIError(msg)
                raise  # 恒久的エラーはそのまま伝播
