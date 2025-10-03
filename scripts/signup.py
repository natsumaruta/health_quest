from peewee import IntegrityError
from models.user import User
from db_config import db


def signup(username, password, email=None):
    db.connect(reuse_if_open=True)
    try:
        user = User.create_user(username=username, password=password, email=email)
        print(f"✅ ユーザー作成: id={user.id}, username={user.username}")
    except IntegrityError as e:
        print("❌ そのユーザー名またはメールは既に登録済みです。")
    finally:
        db.close()


if __name__ == "__main__":
    # デモ：好きに書き換えてOK
    signup(username="chiwawa", password="minipassword", email="chiwawa@example.com")

# 実行するとき：python -m scripts.signup
