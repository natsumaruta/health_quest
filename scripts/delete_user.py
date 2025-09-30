# scripts/delete_user.py
import sys
import os
from models.user import User
from db_config import db


def delete_user(username: str) -> None:
    db.connect(reuse_if_open=True)
    try:
        u = User.get(User.username == username)
        u.delete_instance()  # その1件を削除
        print(f"✅ ユーザー削除: {username}")
    except User.DoesNotExist:
        print("❌ ユーザーが見つかりません。")
    finally:
        db.close()


def delete_all() -> None:
    db.connect(reuse_if_open=True)
    n = User.delete().execute()  # 全件削除
    db.close()
    print(f"✅ 全ユーザー削除: {n} 件")


if __name__ == "__main__":
    delete_user("maruchi")
    # delete_all()

# 実行するとき：python -m scripts.delete_user
