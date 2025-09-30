# routes/ocr.py
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, make_response
from utils.auth_guard import login_required
from services.ocr_service import ocr_ephemeral_from_filestorage
from services.advice_service import analyze_values

ocr_bp = Blueprint("ocr", __name__)


# 1) アップロード画面（フォーム）
@ocr_bp.get("/upload")
@login_required
def upload_form():
    return render_template("ocr_upload.html")


# 2) アップロード処理 → OCR（画像は保存しない）
@ocr_bp.post("/upload")
@login_required
def upload_ocr():
    f = request.files.get("file")
    if not f:
        return render_template("ocr_upload.html", error="画像ファイルを選択してください。")
    res = ocr_ephemeral_from_filestorage(f)
    if "error" in res:
        return render_template(
            "ocr_upload.html", error="画像の読み込みに失敗しました。別の画像でお試しください。"
        )

    # 数値だけをセッションへ（PIIなし）
    session["ocr_extracted"] = res["values"]
    # 確認画面へ
    return redirect(url_for("ocr.review"))


# 3) 本人確認・修正
@ocr_bp.route("/review", methods=["GET", "POST"])
@login_required
def review():
    values = session.get("ocr_extracted") or {}
    if request.method == "POST":
        # 入力値で上書き（空文字は None に）
        confirmed = {}
        for k in values.keys():
            raw = (request.form.get(k) or "").strip()
            confirmed[k] = float(raw) if raw not in ("", None) else None
        session["ocr_confirmed"] = confirmed
        return redirect(url_for("ocr.analysis"))
    return render_template("review.html", data=values)


# 4) しきい値判定＆コメント表示
@ocr_bp.get("/analysis")
@login_required
def analysis():
    confirmed = session.get("ocr_confirmed") or session.get("ocr_extracted") or {}
    result = analyze_values(confirmed)  # flags, comments, summary を返す
    # キャッシュ抑止（ブラウザに残しにくくする）
    resp = make_response(
        render_template(
            "analysis.html",
            values=confirmed,
            flags=result["flags"],
            comments=result["comments"],
            summary=result["summary"],
        )
    )
    resp.headers["Cache-Control"] = "no-store"
    return resp
