# Excuse App

Djangoフロントエンド + FastAPIバックエンドのWebアプリケーション

## プロジェクト構造

```
excuse/
├── frontend/          # Djangoフロントエンド
├── backend/           # FastAPIバックエンド
├── requirements.txt   # Python依存関係
└── README.md         # このファイル
```

## セットアップ手順

### 1. 仮想環境の作成とアクティベート

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境をアクティベート
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. バックエンド（FastAPI）の起動

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. フロントエンド（Django）の起動

```bash
cd frontend
python manage.py migrate
python manage.py runserver
```

## アクセス方法

- フロントエンド: http://localhost:8000
- バックエンドAPI: http://localhost:8001
- FastAPI自動ドキュメント: http://localhost:8001/docs

## 開発環境

- Python 3.8+
- Django 4.2+
- FastAPI 0.100+
- SQLite（開発用） 