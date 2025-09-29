from models.user import User
from db_config import db

# DBに接続してテーブル作成
db.connect()
db.create_tables([User])

# データを追加（Create）
User.create(username="alice", password="secret123")
User.create(username="bob", password="qwerty")

# データを読み取り（Read）
for u in User.select():
    print(u.id, u.username, u.password)
