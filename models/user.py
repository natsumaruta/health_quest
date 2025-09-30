# ユーザーテーブルを定義して、パスワードを安全に保存し、作成日時も記録する

# SqliteDatabase:SQLite用のデータベース接続クラス
# Peeweeの「基本モデルクラス」
# CharField:文字列を保存するカラム（例: ユーザー名、パスワード）
# DateTimeField:日時を保存するカラム（例: ユーザー作成日、最終ログイン日時）
from peewee import SqliteDatabase, Model, CharField, DateTimeField

# Python標準の日時クラス
from datetime import datetime

# models/__init__.py から db をインポート
from . import db

# passlib :パスワードを安全に扱うためのライブラリ
from passlib.hash import pbkdf2_sha256


class User(Model):
    email = CharField(unique=True, null=True)  # emailは任意にしておく例
    username = CharField(unique=True)
    password_hash = CharField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

    # パスワードをハッシュ化して保存
    @classmethod
    def create_user(cls, username, password, email=None):
        hashed = pbkdf2_sha256.hash(password)
        return cls.create(username=username, email=email, password_hash=hashed)

    # 入力されたパスワードと照合
    def match_password(self, password: str) -> bool:
        return pbkdf2_sha256.verify(password, self.password_hash)
