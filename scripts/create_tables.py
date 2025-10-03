from db_config import db
from models.user import User

if __name__ == "__main__":
    db.connect(reuse_if_open=True)
    db.create_tables([User])
    print("✅ Userテーブルを作成（または既存を確認）しました。")
    db.close()

# 実行するとき：python -m scripts.create_tables
