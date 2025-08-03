from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

from .models import UserProfile

load_dotenv()

# Supabaseクライアントの初期化
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key) if url and key else None

@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    """ユーザー登録"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({"error": "メールアドレスとパスワードが必要です"}, status=400)
        
        # Supabaseでユーザー作成
        if not supabase:
            return JsonResponse({"error": "Supabaseクライアントが初期化されていません"}, status=500)
        
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Djangoユーザーも作成
            username = email.split('@')[0]  # メールアドレスの@前をユーザー名として使用
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # ユーザープロフィール作成
            UserProfile.objects.create(
                user=user,
                supabase_user_id=response.user.id,
                email=email
            )
            
            return JsonResponse({"message": "ユーザー登録が完了しました", "user_id": response.user.id})
        else:
            return JsonResponse({"error": "ユーザー登録に失敗しました"}, status=400)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def signin(request):
    """ユーザーログイン"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({"error": "メールアドレスとパスワードが必要です"}, status=400)
        
        # Supabaseでログイン
        if not supabase:
            return JsonResponse({"error": "Supabaseクライアントが初期化されていません"}, status=500)
        
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Djangoユーザーも認証
            try:
                profile = UserProfile.objects.get(supabase_user_id=response.user.id)
                user = profile.user
                login(request, user)
                return JsonResponse({
                    "message": "ログインしました",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                })
            except UserProfile.DoesNotExist:
                return JsonResponse({"error": "ユーザープロフィールが見つかりません"}, status=404)
        else:
            return JsonResponse({"error": "ログインに失敗しました"}, status=400)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def google_signin(request):
    """Google認証でログイン"""
    try:
        data = json.loads(request.body)
        access_token = data.get('access_token')
        
        if not access_token:
            return JsonResponse({"error": "アクセストークンが必要です"}, status=400)
        
        # SupabaseでGoogle認証
        if not supabase:
            return JsonResponse({"error": "Supabaseクライアントが初期化されていません"}, status=500)
        
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "queryParams": {
                    "access_token": access_token
                }
            }
        })
        
        if response.user:
            # Djangoユーザーも認証
            try:
                profile = UserProfile.objects.get(supabase_user_id=response.user.id)
                user = profile.user
                login(request, user)
                return JsonResponse({
                    "message": "Googleログインしました",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                })
            except UserProfile.DoesNotExist:
                # 新規ユーザーの場合はプロフィールを作成
                username = response.user.email.split('@')[0]
                user = User.objects.create_user(
                    username=username,
                    email=response.user.email,
                    password=None  # Google認証なのでパスワードは不要
                )
                
                UserProfile.objects.create(
                    user=user,
                    supabase_user_id=response.user.id,
                    email=response.user.email
                )
                
                login(request, user)
                return JsonResponse({
                    "message": "Googleアカウントで新規登録しました",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                })
        else:
            return JsonResponse({"error": "Googleログインに失敗しました"}, status=400)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def signout(request):
    """ユーザーログアウト"""
    try:
        # Supabaseでログアウト
        if supabase:
            supabase.auth.sign_out()
        
        # Djangoでログアウト
        logout(request)
        
        return JsonResponse({"message": "ログアウトしました"})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def get_user_info(request):
    """現在のユーザー情報を取得"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            return JsonResponse({
                "user": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "email": request.user.email,
                    "supabase_user_id": profile.supabase_user_id
                }
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({"error": "ユーザープロフィールが見つかりません"}, status=404)
    else:
        return JsonResponse({"error": "ログインしていません"}, status=401)

def auth_page(request):
    """認証ページを表示"""
    return render(request, 'auth_app/auth.html')

def auth_callback(request):
    """OAuth認証のコールバック処理"""
    try:
        # Supabaseから認証情報を取得
        if not supabase:
            return JsonResponse({"error": "Supabaseクライアントが初期化されていません"}, status=500)
        
        # セッションからユーザー情報を取得
        session = supabase.auth.get_session()
        
        if session and session.user:
            # Djangoユーザーも認証
            try:
                profile = UserProfile.objects.get(supabase_user_id=session.user.id)
                user = profile.user
                login(request, user)
                return redirect('/')
            except UserProfile.DoesNotExist:
                # 新規ユーザーの場合はプロフィールを作成
                username = session.user.email.split('@')[0]
                user = User.objects.create_user(
                    username=username,
                    email=session.user.email,
                    password=None
                )
                
                UserProfile.objects.create(
                    user=user,
                    supabase_user_id=session.user.id,
                    email=session.user.email
                )
                
                login(request, user)
                return redirect('/')
        else:
            return JsonResponse({"error": "認証に失敗しました"}, status=400)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
