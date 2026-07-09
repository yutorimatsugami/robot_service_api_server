# Robot Service API Server

案内ロボットサービス用のAPIサーバーです。FastAPIで構築され、Gemini APIと連携します。
**HTTPS対応 (自己署名証明書)** により、Web Audio API (スマホマイク) からの音声送信をサポートしています。

---

## 📋 Requirements / 必要環境

- Python 3.10+
- OpenSSL (証明書作成用)
- [Robot Service Database](https://github.com/yutorimatsugami/robot_service_data_base) (別途起動が必要)

> [!WARNING]
> `google-generativeai` パッケージ (requirements.txt) は Google により非推奨(EOL)となっています。本プロジェクトでは現時点でも使用しており、コード側で該当の非推奨警告を抑制しています (src/main.py, src/gemini_client.py)。使用モデルは `gemini-2.5-flash`。将来的に後継の `google-genai` パッケージへの移行が必要です。

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

> [!TIP]
> `setup.sh` / `setup.ps1` を使えば上記の手順を自動で実行できます。
>
> ```bash
> ./setup.sh      # Linux/macOS
> .\setup.ps1    # Windows
> ```

### 3. Generate SSL Certificates / 証明書の作成 (必須)

スマホのマイク機能(Web Audio API)を使用するため、HTTPS化が必須です。
サーバーのIPアドレスを含んだ自己署名証明書を作成します。

1. IPアドレスを確認 (例: `192.168.11.7` とする)
2. `src/` ディレクトリに移動
3. 設定ファイル `san.cnf` を作成 (IPアドレスを自分の環境に合わせて書き換えること)

```ini
[req]
default_bits  = 2048
distinguished_name = req_distinguished_name
req_extensions = req_ext
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = 192.168.11.7

[req_ext]
subjectAltName = @alt_names

[v3_req]
subjectAltName = @alt_names

[alt_names]
IP.1 = 192.168.11.7
IP.2 = 127.0.0.1
DNS.1 = localhost
```

4. 証明書を生成

```bash
# srcディレクトリ内で実行
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem -config san.cnf
```

> [!CAUTION]
> `san.cnf` には環境固有のIPアドレスが直接記述されるため、リポジトリにはコミットしないでください (`.gitignore` で除外済み)。

### 4. Configure / 設定

`.env` ファイルを編集し、必要な情報を入力 (詳細は `.env.example` を参照):
```ini
DATABASE_URL=postgresql://robot_user:robot_pass@localhost:5432/robot_service_db
GEMINI_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8000
```
> `HOST` / `PORT` は `run.sh` / `run.ps1` がサーバー起動時のバインド先として参照します (未設定時は `0.0.0.0:8000` がデフォルト)。

### 5. Run (HTTPS) / 起動

証明書ファイルを指定して起動します。
IPアドレスが変わった場合は証明書を作り直す必要があります。

**スクリプトで起動（推奨）:**
```bash
./run.sh      # Linux/macOS
.\run.ps1    # Windows
```

**または手動で:**
```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

---

## ⚠️ Browser Security Warning / ブラウザでのセキュリティ警告

自己署名証明書を使用しているため、ブラウザでアクセスすると「安全ではありません」という警告が出ます。
WebアプリからAPIを利用するためには、**事前に一度ブラウザでアクセスして例外許可を与える**必要があります。

1. スマホ/PCのブラウザで `https://[サーバーIP]:8000/docs` にアクセス。
2. 警告画面で「詳細設定」→「[サーバーIP]に進む（安全ではありません）」を選択。
3. Swagger UIが表示されればOK。これでAPIが呼び出せるようになります。

---

## 🔌 API Endpoints / エンドポイント

| Method | Endpoint | 説明 |
|--------|----------|------|
| GET | `/` | ヘルスチェック |
| GET | `/ads` | 広告一覧取得 |
| GET | `/timetable/{station_name}` | **時刻表検索** (駅名指定、時刻フィルタ可) |
| POST | `/chat` | テキストチャット (Gemini連携) |
| POST | `/voice_chat` | **音声チャット** (音声ファイル受信→文字起こし→回答) |

### /chat・/voice_chat の応答フロー

`/chat` および `/voice_chat` は、以下の2段階のパイプラインで応答テキストを生成します:

- **1. FAQキーワード検索**: DB内のFAQ (`trigger_keywords`) とユーザー発話をキーワード一致で照合し、該当するFAQがあればその回答をそのまま返します (単純な部分一致であり、厳密な完全一致ではありません、src/crud.py の `get_faq_response`)。ただし「時間」「何時」「時刻表」等の時刻表関連キーワードを含む場合はFAQ検索自体をスキップします。
- **2. Geminiフォールバック**: FAQに該当しない場合、Gemini (`gemini-2.5-flash`) にFunction Calling付きで問い合わせます。時刻表に関する質問はGeminiが `get_timetable_info` ツールを呼び出し、内部で時刻表DBを検索した結果を踏まえて回答を生成します (src/main.py:84-101, src/gemini_client.py)。

### POST /chat
テキストメッセージを送信し、チャット応答を取得します (リクエストボディは `src/schemas.py` の `ChatRequest`)。

| パラメータ (body) | 説明 | デフォルト |
|-----------|------|-----------|
| `message` (str) | ユーザーの発話テキスト | 必須 |
| `user_id` (str, 任意) | ユーザー識別子 | `"guest"` |
| `lang` (str, 任意) | 応答言語 (`"ja"` または `"en"`) | `"ja"` |

```bash
curl -X POST "https://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "京都行きは何時ですか", "user_id": "guest", "lang": "ja"}' \
  --insecure
```

### GET /timetable/{station_name}
指定した駅への時刻表を取得します。

| パラメータ | 説明 | デフォルト |
|-----------|------|-----------|
| `station_name` (path) | 行先駅名 (例: 京都) | 必須 |
| `time` (query) | 検索開始時刻 (HH:MM) | 現在時刻 |

```bash
# 京都方面の時刻表（現在時刻以降）
curl "https://localhost:8000/timetable/京都" --insecure

# 10:00以降の時刻表を取得
curl "https://localhost:8000/timetable/京都?time=10:00" --insecure
```

### POST /voice_chat
Web Audio API等で録音した `wav` ファイルをアップロードします。

| パラメータ | 説明 | デフォルト |
|-----------|------|-----------|
| `audio` (form, file) | 録音した音声ファイル (wav) | 必須 |
| `lang` (query) | 文字起こし・応答言語 (`"ja"` または `"en"`) | `"ja"` |

```bash
curl -X POST "https://localhost:8000/voice_chat?lang=ja" \
  -F "audio=@recording.wav" \
  --insecure
```

---

## ⚙️ Configuration / 設定

CORS設定は `src/main.py` 内で、サーバー自身のIPアドレスを自動取得して `https://[IP]:1880` (Node-RED) を許可リストに含めるよう動的に構成されています。

> [!CAUTION]
> ただし現状の `origins` リストには開発用として `"*"` (全オリジン許可) も含まれており、かつ `allow_credentials=True` と併用されているため、**実際には全てのオリジンからのアクセスが許可されてしまっています** (src/main.py:36-42)。本番運用前には `src/main.py` の `origins` から `"*"` を削除し、Node-RED (`https://<IP>:1880`) など必要なオリジンのみに制限してください。

なお、本APIは兄弟プロジェクト [`nodered_json_with_python`](../nodered_json_with_python) のNode-RED UIから利用されており、そのフローが `https://<このサーバーのIP>:8000/chat` および `/voice_chat` を呼び出します。

---

## 📁 Project Structure / プロジェクト構成

```
robot_service_api_server/
├── requirements.txt      # Python依存関係
├── .env.example          # 環境変数テンプレート
├── .env                  # 環境変数 (Git管理外)
├── .gitignore            # Git管理外ファイル設定
├── README.md
├── setup.sh / setup.ps1  # セットアップスクリプト
├── run.sh / run.ps1      # 起動スクリプト (HTTPS対応)
└── src/
    ├── main.py           # FastAPIアプリ
    ├── database.py       # DB接続
    ├── models.py         # SQLAlchemyモデル
    ├── schemas.py        # Pydanticスキーマ
    ├── crud.py           # DB操作
    ├── gemini_client.py  # Gemini API連携
    ├── prompt.py         # プロンプトテンプレート管理
    ├── san.cnf           # SSL証明書設定 (IP変更時に編集)
    ├── cert.pem          # SSL証明書 (Git管理外)
    └── key.pem           # SSL秘密鍵 (Git管理外)
```

---

## 🚫 .gitignore / Git管理外ファイル

以下のファイルはセキュリティ上の理由でGit管理外です:

| ファイル | 理由 |
|---------|------|
| `.env` | APIキーなどの機密情報を含む |
| `*.pem` | SSL証明書・秘密鍵 |
| `venv/` | Python仮想環境 |
| `__pycache__/` | Pythonキャッシュ |

---

## 📝 License

MIT License（LICENSEファイルは未同梱）

