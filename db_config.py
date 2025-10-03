# ここで「どのDBに接続するか」を決めて、アプリ全体で共通して使う

# ログ出力や環境変数の操作に使う標準ライブラリを読み込む
import logging
import os

# Peewee で SQLite データベースを使うためのクラスを読み込む
from peewee import SqliteDatabase

# python-dotenv ライブラリから、.env ファイルを読み込む関数をインポート
# → APIキーやDBの接続先など「秘密情報」を環境変数に設定できる
from dotenv import load_dotenv

# .env ファイルを読み込み、環境変数として登録する
# 例: .env に DATABASE="sqlite:///app.db" と書いておくと、
# os.environ["DATABASE"] でその値が取れるようになる
load_dotenv()

# Peewee が実行する SQL を確認できるようにログを設定する
logger = logging.getLogger("peewee")  # Peewee 用のロガーを作成
logger.addHandler(logging.StreamHandler())  # ログの出力先をコンソールに設定
logger.setLevel(logging.DEBUG)  # DEBUG レベル以上のログを出力するように設定

# 環境変数から DB の接続URL を取得
# os.environ.get("DATABASE") → 環境変数 DATABASE の値を返す
# 値がなければ or の右側 "sqlite:///peewee_db.sqlite" を使う
db = os.environ.get("DATABASE") or "sqlite:///peewee_db.sqlite"

# Peewee 用に SQLite の接続を準備する
# URL が "sqlite:///" から始まる場合、その後ろのパス部分を取り出す
# 例: "sqlite:///peewee_db.sqlite" → "peewee_db.sqlite"
if db.startswith("sqlite:///"):
    db_path = db.replace("sqlite:///", "")  # パス部分だけを抽出
    db = SqliteDatabase(db_path)  # Peewee の SQLite 用クラスで接続を作成
else:
    # もし SQLite 以外の URL が来た場合はサポートしていないのでエラーにする
    raise ValueError("サポートされていないDB URLです")
