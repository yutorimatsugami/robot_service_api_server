# Robot Service API Server

案内ロボットサービス用のAPIサーバーです。FastAPIで構築され、Gemini APIと連携します。
**HTTPS対応 (自己署名証明書)** により、Web Audio API (スマホマイク) からの音声送信をサポートしています。

---

## 📋 Requirements / 必要環境

- Python 3.10+
- OpenSSL (証明書作成用)
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

### 4. Configure / 設定

`.env` ファイルを編集し、必要な情報を入力:
```ini
DATABASE_URL=postgresql://robot_user:robot_pass@localhost:5432/robot_service_db
GEMINI_API_KEY=your_api_key_here
```

### 5. Run (HTTPS) / 起動

証明書ファイルを指定して起動します。
IPアドレスが変わった場合は証明書を作り直す必要があります。

```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

※ `run.sh` / `run.ps1` はHTTP用設定のままの場合がありますので、上記の手動コマンド推奨。

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
| POST | `/chat` | テキストチャット (Gemini連携) |
| POST | `/voice_chat` | **音声チャット** (音声ファイル受信→文字起こし→回答) |

### POST /voice_chat
Web Audio API等で録音した `wav` ファイルをアップロードします。

```bash
curl -X POST "https://localhost:8000/voice_chat" \
  -F "audio=@recording.wav" \
  --insecure
```

---

## ⚙️ Configuration / 設定

CORS設定は `main.py` 内で、サーバー自身のIPアドレスを自動取得して `https://[IP]:1880` (Node-RED) からのアクセスを許可するように動的に構成されています。

---

## 📝 License

MIT License
