# routes/core.py
from flask import Blueprint
from db_config import db

# このBlueprint自身はルートを持たず、フックだけ担当
core_bp = Blueprint("core", __name__)


# -----------------------------
# Peewee のDB接続ライフサイクル
# Flaskはリクエストごとに処理するので、
# 毎回 DB 接続を開いて → 終わったら閉じる のが安全
# -----------------------------
@core_bp.before_request
def _db_connect():
    if db.is_closed():
        db.connect(reuse_if_open=True)


@core_bp.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()
