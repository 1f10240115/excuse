import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 環境変数を読み込み
load_dotenv()

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')

print(f"URL: {url}")
print(f"Key: {key[:20]}..." if key else "Key: None")

try:
    # Supabaseクライアントを作成
    supabase: Client = create_client(url, key)
    print("✅ Supabaseクライアント作成成功")
    
    # テーブル一覧を取得
    print("\n📋 テーブル一覧:")
    response = supabase.table('excuses').select('*').limit(1).execute()
    print(f"excusesテーブル: {len(response.data)}件のデータ")
    
    # サンプルデータを挿入
    print("\n📝 サンプルデータを挿入中...")
    test_data = {
        'title': 'テスト言い訳',
        'description': 'これはテスト用の言い訳です',
        'category': 'テスト'
    }
    
    insert_response = supabase.table('excuses').insert(test_data).execute()
    print(f"✅ データ挿入成功: {insert_response.data}")
    
    # 全データを取得
    print("\n📊 全データ:")
    all_data = supabase.table('excuses').select('*').execute()
    for item in all_data.data:
        print(f"- {item['id']}: {item['title']} ({item['category']})")
        
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc() 