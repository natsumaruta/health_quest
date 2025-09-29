import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from db_config import db
from models.user import User  # create_user / match_password を使う

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")


# ---- Peewee の接続ライフサイクル（重要）----
@app.before_request
def _db_connect():
    if db.is_closed():
        db.connect(reuse_if_open=True)


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


# -------------------------------------------


def login_required(view):
    # 超シンプルなログイン必須デコレータ
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("ログインしてください", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def index():
    # ログインしてたらダッシュボードへ
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip() or None
        password = request.form.get("password", "")

        if not username or not password:
            flash("ユーザー名とパスワードは必須です", "danger")
            return render_template("signup.html")

        # 既存チェック（usernameユニーク）
        if User.select().where(User.username == username).exists():
            flash("そのユーザー名は既に使われています", "danger")
            return render_template("signup.html")

        # 作成
        user = User.create_user(username=username, password=password, email=email)
        flash("サインアップ完了！ログインしてください", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            user = User.get(User.username == username)
        except User.DoesNotExist:
            flash("ユーザーが見つかりません", "danger")
            return render_template("login.html")

        if user.match_password(password):
            # セッションに格納
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"ようこそ、{user.username} さん！", "success")
            # 更新日時もついでに更新
            user.updated_at = datetime.now()
            user.save(only=[User.updated_at])
            return redirect(url_for("dashboard"))
        else:
            flash("パスワードが違います", "danger")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))


if __name__ == "__main__":
    app.run(debug=True)
