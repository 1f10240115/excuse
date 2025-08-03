# Vercelデプロイ手順

## 1. Vercel CLIのインストール

```bash
npm install -g vercel
```

## 2. Vercelにログイン

```bash
vercel login
```

## 3. 環境変数の設定

Vercelダッシュボードで以下の環境変数を設定してください：

### Supabase設定
- `SUPABASE_URL`: SupabaseプロジェクトのURL
- `SUPABASE_KEY`: Supabaseのanon public key
- `SUPABASE_SERVICE_KEY`: Supabaseのservice role secret key

### Django設定
- `SECRET_KEY`: Djangoのシークレットキー（ランダムな文字列）
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `.vercel.app`

### Gemini API設定（オプション）
- `GEMINI_API_KEY`: Gemini APIキー

## 4. デプロイ

```bash
vercel
```

## 5. 本番環境へのデプロイ

```bash
vercel --prod
```

## 注意事項

1. **データベース**: Supabaseを使用しているため、データベースはクラウド上で動作します
2. **静的ファイル**: Djangoの静的ファイルは自動的に処理されます
3. **CORS**: Vercelドメインからのアクセスを許可するように設定済み
4. **環境変数**: 本番環境では必ず環境変数を設定してください

## トラブルシューティング

### よくある問題

1. **環境変数が設定されていない**
   - Vercelダッシュボードで環境変数を確認
   - 本番環境とプレビュー環境の両方に設定が必要

2. **CORSエラー**
   - フロントエンドとバックエンドのドメインが正しく設定されているか確認

3. **データベース接続エラー**
   - Supabaseの設定が正しいか確認
   - ネットワークアクセスが許可されているか確認 