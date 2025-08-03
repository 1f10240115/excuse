#!/usr/bin/env python3
"""
ユーザー別データのテストスクリプト
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# 環境変数を読み込み
load_dotenv()

# Supabaseクライアントの初期化
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Error: Supabase環境変数が設定されていません")
    sys.exit(1)

supabase = create_client(url, key)

def test_user_data():
    """ユーザー別データのテスト"""
    print("=== ユーザー別データテスト ===")
    
    # テスト用のユーザーID（実際のSupabaseユーザーIDに置き換えてください）
    test_user_id = "your-test-user-id"
    
    # 1. ユーザー別の言い訳を作成
    print("\n1. テストユーザーの言い訳を作成...")
    test_excuse = {
        "title": "テスト言い訳",
        "description": "これはテスト用の言い訳です",
        "category": "テスト",
        "user_id": test_user_id
    }
    
    try:
        response = supabase.table('excuses').insert(test_excuse).execute()
        print(f"作成成功: {response.data}")
    except Exception as e:
        print(f"作成エラー: {e}")
    
    # 2. ユーザー別の言い訳を取得
    print("\n2. テストユーザーの言い訳を取得...")
    try:
        response = supabase.table('excuses').select('*').eq('user_id', test_user_id).execute()
        print(f"取得成功: {len(response.data)}件の言い訳")
        for excuse in response.data:
            print(f"  - {excuse['title']}: {excuse['description']}")
    except Exception as e:
        print(f"取得エラー: {e}")
    
    # 3. 全ユーザーの言い訳を取得（管理者用）
    print("\n3. 全ユーザーの言い訳を取得...")
    try:
        response = supabase.table('excuses').select('*').execute()
        print(f"取得成功: {len(response.data)}件の言い訳")
        for excuse in response.data:
            print(f"  - ユーザー{excuse['user_id']}: {excuse['title']}")
    except Exception as e:
        print(f"取得エラー: {e}")

if __name__ == "__main__":
    test_user_data() 