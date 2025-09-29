from models.user import User
from db_config import db


def login(username, password):
    db.connect(reuse_if_open=True)
    try:
        user = User.get(User.username == username)
    except User.DoesNotExist:
        print("❌ ユーザーが見つかりません。")
        db.close()
        return

    if user.match_password(password):
        print("✅ ログイン成功！")
    else:
        print("❌ パスワードが違います。")
    db.close()


if __name__ == "__main__":
    # デモ：signup.pyで作ったユーザーで試す
    login(username="kisyuuinu", password="mepassword")

# 実行するとき：python -m scripts.login
