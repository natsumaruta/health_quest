# scripts/update_user.py
import sys
import os
from peewee import IntegrityError
from models.user import User
from db_config import db
from passlib.hash import bcrypt  # パスワード更新用


def update_username(old_username: str, new_username: str) -> None:
    db.connect(reuse_if_open=True)
    try:
        u = User.get(User.username == old_username)
        u.username = new_username
        u.save(only=[User.username])  # 1件のUPDATE
        print(f"✅ username更新: {old_username} → {new_username}")
    except User.DoesNotExist:
        print("❌ ユーザーが見つかりません。")
    except IntegrityError:
        print("❌ そのusernameは既に使われています。")
    finally:
        db.close()


def update_email(username: str, new_email: str) -> None:
    db.connect(reuse_if_open=True)
    try:
        u = User.get(User.username == username)
        u.email = new_email
        u.save(only=[User.email])
        print(f"✅ email更新: {username} → {new_email}")
    except User.DoesNotExist:
        print("❌ ユーザーが見つかりません。")
    except IntegrityError:
        print("❌ そのemailは既に使われています。")
    finally:
        db.close()


def update_password(username: str, new_password: str) -> None:
    db.connect(reuse_if_open=True)
    try:
        u = User.get(User.username == username)
        u.password_hash = bcrypt.hash(new_password)  # ハッシュ化して保存
        u.save(only=[User.password_hash])
        print(f"✅ パスワード更新: {username}")
    except User.DoesNotExist:
        print("❌ ユーザーが見つかりません。")
    finally:
        db.close()


if __name__ == "__main__":
    # ★動作確認用の例。必要に応じて書き換えて実行してね。
    # 1) ユーザー名の変更
    update_username(old_username="chiwawa", new_username="maruchi")

    # 2) メールの変更
    update_email(username="maruchi", new_email="maruchi@example.com")

    # 3) パスワードの変更
    update_password(username="maruchi", new_password="newpass789")

# 実行するとき：python -m scripts.update_user
