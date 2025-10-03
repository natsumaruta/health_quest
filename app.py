# app.py
import os
from flask import Flask
from dotenv import load_dotenv
from routes.core import core_bp
from routes.auth import auth_bp
from routes.ocr import ocr_bp


# -----------------------------
# .envファイルから環境変数を読み込む
# -----------------------------
load_dotenv()

app = Flask(__name__)

# Flaskのセッション用の暗号化キー
# .env に SECRET_KEY がなければ "dev-secret-change-me" を使う
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

# 推奨設定（本番想定）
app.config.update(
    JSON_AS_ASCII=False,  # JSONの日本語対応（JSON_AS_ASCII=False）を入れておく
    MAX_CONTENT_LENGTH=10
    * 1024
    * 1024,  # アップロードできるリクエストサイズの上限を指定（ここでは 10MB）.画像アップロードで「巨大ファイル送られてサーバが落ちる」みたいな事故を防ぐ
    SESSION_COOKIE_HTTPONLY=True,  # セッションIDを保存するCookieを JavaScriptから読めなくする 設定
    SESSION_COOKIE_SAMESITE="Lax",  # Cookieを「どんな場面でブラウザが送信するか」を決める設定
    SESSION_COOKIE_SECURE=False,  # 本番は SESSION_COOKIE_SECURE=True にする（HTTPS前提）。ローカル開発中は False、HTTPS本番は True
)

# まず最初に core_bp を登録（全リクエストでDBフックが効く）
app.register_blueprint(core_bp)

# Blueprint登録
app.register_blueprint(auth_bp, url_prefix="/")
app.register_blueprint(ocr_bp, url_prefix="/ocr")  # 例）/ocr/ephemeral


# -----------------------------
# エントリーポイント
# -----------------------------
if __name__ == "__main__":
    # debug=True → コード変更すると自動リロードされる
    app.run(debug=True)
