from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
import json

# FastAPIバックエンドのベースURL
API_BASE_URL = "http://localhost:8001"

def index(request):
    """メインページを表示"""
    return render(request, 'excuses/index.html')

@require_http_methods(["GET"])
def get_excuses(request):
    """全ての言い訳を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/excuses")
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
        response = requests.post(f"{API_BASE_URL}/api/excuses", json=data)
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
