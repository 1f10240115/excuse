# Google認証の設定手順

## 1. Google Cloud Consoleでの設定

### 1.1 OAuth 2.0クライアントIDを作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. プロジェクトを作成または選択
3. **APIとサービス** → **認証情報**に移動
4. **認証情報を作成** → **OAuth 2.0クライアントID**を選択
5. アプリケーションの種類で**ウェブアプリケーション**を選択
6. 以下の設定を行う：
   - **承認済みのリダイレクトURI**:
     - `https://your-project.supabase.co/auth/v1/callback`
     - `http://localhost:8000/auth/callback/`（開発用）

### 1.2 必要なAPIを有効化

1. **APIとサービス** → **ライブラリ**に移動
2. 以下のAPIを有効化：
   - Google+ API
   - Google Identity API

## 2. Supabaseでの設定

### 2.1 Google認証プロバイダーを有効化

1. Supabaseダッシュボードにアクセス
2. **Authentication** → **Providers**に移動
3. **Google**を有効にする
4. Google Cloud Consoleで取得した**Client ID**と**Client Secret**を入力
5. **保存**をクリック

### 2.2 リダイレクトURLの設定

**Site URL**に以下を設定：
- 本番環境: `https://your-domain.com`
- 開発環境: `http://localhost:8000`

## 3. 環境変数の設定

`.env`ファイルに以下を追加：

```env
# Supabase設定
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Google認証設定（オプション）
GOOGLE_CLIENT_ID=your-google-client-id
```

## 4. フロントエンドの設定

### 4.1 認証ページの設定

`frontend/auth_app/templates/auth_app/auth.html`の以下の部分を更新：

```javascript
// Google Identity Servicesを使用する場合
client_id: 'YOUR_GOOGLE_CLIENT_ID', // 実際のクライアントIDに置き換え
```

### 4.2 簡単な認証ページの設定

`frontend/auth_app/templates/auth_app/auth_simple.html`の以下の部分を更新：

```javascript
const supabaseUrl = 'YOUR_SUPABASE_URL';
const supabaseKey = 'YOUR_SUPABASE_ANON_KEY';
```

## 5. テスト手順

1. Djangoサーバーを起動：
   ```bash
   cd frontend
   python manage.py runserver
   ```

2. 認証ページにアクセス：
   - `http://localhost:8000/auth/auth/`

3. Googleログインボタンをクリックしてテスト

## 6. トラブルシューティング

### 6.1 よくあるエラー

- **"redirect_uri_mismatch"**: リダイレクトURIが正しく設定されていない
- **"invalid_client"**: クライアントIDまたはシークレットが間違っている
- **"access_denied"**: ユーザーが認証をキャンセルした

### 6.2 デバッグ方法

1. ブラウザの開発者ツールでネットワークタブを確認
2. Supabaseダッシュボードの**Logs**でエラーログを確認
3. Djangoのログでエラーを確認

## 7. セキュリティ考慮事項

- 本番環境ではHTTPSを使用
- 適切なCORS設定を行う
- 環境変数は安全に管理
- 定期的にアクセストークンを更新 