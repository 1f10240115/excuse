from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import requests
import json

# FastAPIバックエンドのベースURL
API_BASE_URL = "http://localhost:8001"

def index(request):
    """メインページを表示"""
    if not request.user.is_authenticated:
        return redirect('/auth/auth/')
    return render(request, 'excuses/index.html')

@require_http_methods(["GET"])
def get_excuses(request):
    """ユーザーの言い訳を取得"""
    try:
        if request.user.is_authenticated:
            # ユーザーがログインしている場合、そのユーザーの言い訳のみ取得
            user_id = request.user.profile.supabase_user_id
            response = requests.get(f"{API_BASE_URL}/api/excuses?user_id={user_id}")
        else:
            # 未ログインの場合は空のリストを返す
            return JsonResponse([], safe=False)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def get_excuse(request, excuse_id):
    """指定されたIDの言い訳を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/excuses/{excuse_id}")
        response.raise_for_status()
        return JsonResponse(response.json())
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_excuse(request):
    """新しい言い訳を作成"""
    try:
        data = json.loads(request.body)
        
        if not request.user.is_authenticated:
            return JsonResponse({"error": "ログインが必要です"}, status=401)
        
        # フロントエンドから送られてくるデータを適切な形式に変換
        excuse_data = {
            "title": data.get("detailedDescription", "新しい言い訳"),
            "description": data.get("detailedDescription", "詳細な説明"),
            "category": data.get("category", "その他"),
            "user_id": request.user.profile.supabase_user_id
        }
        
        response = requests.post(f"{API_BASE_URL}/api/excuses", json=excuse_data)
        response.raise_for_status()
        return JsonResponse(response.json())
    except (json.JSONDecodeError, requests.RequestException) as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def get_categories(request):
    """利用可能なカテゴリを取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/categories")
        response.raise_for_status()
        return JsonResponse(response.json())
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_excuse(request):
    """Gemini APIを使用して言い訳を生成"""
    try:
        response = requests.post(f"{API_BASE_URL}/generate_excuse")
        response.raise_for_status()
        return JsonResponse(response.json())
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)
