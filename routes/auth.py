# routes/auth.py
# Blueprint：Flask が持っている モジュール化の仕組み。ルートや機能をまとめて分割管理可能。
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User  # Userモデル（create_user / match_password を利用）
from utils.auth_guard import login_required


auth_bp = Blueprint("auth", __name__)


# -----------------------------
# トップページ
# ログイン済みならダッシュボードへ飛ばす
# -----------------------------
@auth_bp.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("auth.dashboard"))
    return render_template("index.html")


# -----------------------------
# サインアップ（新規登録）
# -----------------------------
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip() or None
        password = request.form.get("password", "")

        # バリデーション（必須チェック）
        if not username or not password:
            flash("ユーザー名とパスワードは必須です", "danger")
            return render_template("signup.html")

        # username の重複チェック
        if User.select().where(User.username == username).exists():
            flash("そのユーザー名は既に使われています", "danger")
            return render_template("signup.html")

        # ユーザーをDBに作成
        User.create_user(username=username, password=password, email=email)
        flash("サインアップ完了！ログインしてください", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


# -----------------------------
# ログイン処理
# -----------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # DBからユーザーを探す
        try:
            user = User.get(User.username == username)
        except User.DoesNotExist:
            flash("ユーザーが見つかりません", "danger")
            return render_template("login.html")

        # パスワード一致チェック
        if user.match_password(password):
            # セッションにユーザー情報を保存（ログイン状態を維持）
            session["user_id"] = user.id
            session["username"] = user.username

            flash(f"ようこそ、{user.username} さん！", "success")

            # 更新日時を更新（最終ログイン時刻の代わり）
            user.updated_at = datetime.now()
            user.save(only=[User.updated_at])

            return redirect(url_for("auth.dashboard"))
        else:
            flash("パスワードが違います", "danger")
            return render_template("login.html")

    return render_template("login.html")


# -----------------------------
# ログアウト処理
# -----------------------------
@auth_bp.route("/logout")
def logout():
    # セッションを空にする → ログイン状態を解除
    session.clear()
    flash("ログアウトしました", "info")
    return redirect(url_for("auth.index"))


# -----------------------------
# ダッシュボード（ログイン必須）
# -----------------------------
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))
