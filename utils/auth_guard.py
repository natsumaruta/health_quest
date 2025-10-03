# utils/auth_guard.py
# routes/auth.py と routes/ocr.py のどちらからでも、
# from utils.auth_guard import login_required で使えるようにする

from functools import wraps
from flask import session, redirect, url_for, flash


# -----------------------------
# ログイン必須デコレータ（Flask-Loginを使わない簡易版）
# session["user_id"] が無ければログインページへリダイレクト
# -----------------------------
def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("ログインしてください", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped
