# Robot Service API Server

案内ロボットサービス用のAPIサーバーです。FastAPIで構築され、Gemini APIと連携します。

---

## 📋 Requirements / 必要環境

- Python 3.10+
- [Robot Service Database](https://github.com/yutorimatsugami/robot_service_data_base) (別途起動が必要)

---

## 🚀 Quick Start / クイックスタート

### 1. Clone & Setup / クローンとセットアップ

```bash
git clone https://github.com/yutorimatsugami/robot_service_api_server.git
cd robot_service_api_server
```

### 2. Setup Environment / 環境セットアップ

**Linux / macOS:**
```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
.\venv\Scripts\Activate.ps1

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 3. Configure / 設定

`.env` ファイルを編集し、必要な情報を入力:
```ini
DATABASE_URL=postgresql://robot_user:robot_pass@localhost:5432/robot_service_db
GEMINI_API_KEY=your_api_key_here
```

### 4. Run / 起動

**Linux / macOS:**
```bash
./run.sh
```

**Windows (PowerShell):**
```powershell
.\run.ps1
```

**または手動で:**
```bash
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\Activate.ps1  # Windows
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access / アクセス

| URL | 説明 |
|-----|------|
| http://localhost:8000 | API Root |
| http://localhost:8000/docs | Swagger UI (API ドキュメント) |
| http://localhost:8000/redoc | ReDoc |

---

## 📁 Project Structure / プロジェクト構成

```
robot_service_api_server/
├── requirements.txt      # Python依存関係
├── .env.example          # 環境変数テンプレート
├── .env                  # 環境変数 (Git管理外)
├── .gitignore
├── README.md
├── setup.sh / setup.ps1  # セットアップスクリプト
├── run.sh / run.ps1      # 起動スクリプト
└── src/
    ├── main.py           # FastAPIアプリ
    ├── database.py       # DB接続
    ├── models.py         # SQLAlchemyモデル
    ├── schemas.py        # Pydanticスキーマ
    ├── crud.py           # DB操作
    └── gemini_client.py  # Gemini API連携
```

---

## 🔌 API Endpoints / エンドポイント

| Method | Endpoint | 説明 |
|--------|----------|------|
| GET | `/` | ヘルスチェック |
| GET | `/ads` | 広告一覧取得 |
| POST | `/chat` | AI チャット (Gemini連携) |

### POST /chat
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "おすすめのお店を教えて"}'
```

---

## ⚙️ Configuration / 設定

| 環境変数 | 説明 | 例 |
|---------|------|-----|
| `DATABASE_URL` | DB接続URL | `postgresql://user:pass@host:5432/db` |
| `GEMINI_API_KEY` | Gemini APIキー | `AIza...` |
| `HOST` | サーバーホスト | `0.0.0.0` |
| `PORT` | サーバーポート | `8000` |

---

## 🤝 Contributing / 貢献

1. Fork this repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📝 License

MIT License
