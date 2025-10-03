# routes/ocr.py
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, make_response
from utils.auth_guard import login_required
from services.ocr_service import ocr_ephemeral_from_filestorage
from services.advice_service import analyze_values
from services.date_utils import extract_dates

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
    if not f or not getattr(f, "filename", ""):
        return render_template("ocr_upload.html", error="画像ファイルを選択してください。")

    # 簡易MIMEチェック
    if f.mimetype not in ("image/png", "image/jpeg", "image/webp", "application/pdf"):
        return render_template("ocr_upload.html", error="対応形式は PNG/JPEG/WebP/PDF です。")

    # 容量（サーバ側でも MAX_CONTENT_LENGTH を設定済みだと尚良し）
    f.seek(0, 2)  # end
    size = f.tell()
    f.seek(0)
    if size > 10 * 1024 * 1024:
        return render_template("ocr_upload.html", error="ファイルが大きすぎます（10MBまで）。")


    res = ocr_ephemeral_from_filestorage(f)
    if "error" in res:
        return render_template(
            "ocr_upload.html", error="画像の読み込みに失敗しました。別の画像でお試しください。"
        )

    # デバッグ行（なければ空配列）
    debug_lines = res.get("debug_lines", [])
    session["ocr_debug_lines"] = debug_lines

    # 年抽出（文字列を渡す想定）
    text = "\n".join(debug_lines)
    years = sorted({dt.year for dt in extract_dates(text)}, reverse=True)
    session["ocr_years"] = years
    session["ocr_target_year"] = years[0] if years else None

    session["ocr_extracted"] = res.get("values", {})
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
    if not confirmed:
        return redirect(url_for("ocr.upload_form"))
    result = analyze_values(confirmed)
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
