# services/ocr_service.py
import io, re
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
from datetime import datetime

import paddle

paddle.set_device("cpu")

# ローカルモデルを明示指定（自動DLを回避）
_ocr = PaddleOCR(
    use_gpu=False,
    use_angle_cls=True,
    lang="japan",
    det_model_dir="models/det",
    cls_model_dir="models/cls",
    rec_model_dir="models/rec_japan",
    show_log=False,
)

FIELD_PATS = {
    "sbp": [r"収縮期血圧", r"最高血圧", r"上の血圧"],
    "dbp": [r"拡張期血圧", r"最低血圧", r"下の血圧"],
    "tg": [r"中性脂肪", r"TG", r"トリグリセリド"],
    "ldl": [r"LDL"],
    "hba1c": [r"HbA1c", r"ヘモグロビンA1c"],
    "cre": [r"クレアチニン", r"CRE"],
    "egfr": [r"eGFR"],
    "ua": [r"尿酸", r"UA"],
}
PII_DENY = [
    r"氏名",
    r"名前",
    r"住所",
    r"TEL|電話",
    r"生年月日",
    r"\d{4}年\d{1,2}月\d{1,2}日",
    r"ｶﾅ|カナ|ﾌﾘｶﾞﾅ",
]

UNIT_PAT = r"(mg/dL|mmHg|%|g/dL|mL/min/1\.73m²)"
NUM_PAT = r"[-0-9０-９\.,．]+"


def _safe_float(s: str):
    if not s:
        return None
    s = re.sub(UNIT_PAT, "", s, flags=re.IGNORECASE)
    s = s.replace("．", ".").replace(",", "").strip()
    s = s.translate(str.maketrans("０１２３４５６７８９．－", "0123456789.-"))
    try:
        return float(s)
    except:
        return None


def _is_pii(text: str) -> bool:
    return any(re.search(p, text) for p in PII_DENY)


def ocr_ephemeral_from_filestorage(file_storage) -> dict:
    """画像はディスク保存せず、PII除外して数値だけ返す。OpenCVは使わない。"""
    try:
        raw = file_storage.read()
        img = Image.open(io.BytesIO(raw)).convert("RGB")

        # （任意の前処理）
        # img = img.convert("L").resize((img.width*2, img.height*2)).convert("RGB")

        np_img = np.array(img)
    except Exception as e:
        return {"error": f"decode_failed: {e}"}

    result = _ocr.ocr(np_img, cls=True)

    lines = []
    for block in result:
        for item in block:
            text, conf = item[1][0], float(item[1][1])
            if conf < 0.2:
                continue
            if _is_pii(text):
                continue
            lines.append(text)

    joined = "\n".join(lines)
    out = {k: None for k in FIELD_PATS.keys()}

    for key, pats in FIELD_PATS.items():
        m = re.search(
            r"(" + "|".join(pats) + r")\s*[:：]?\s*(" + NUM_PAT + r")\s*(" + UNIT_PAT + r")?",
            joined,
            flags=re.IGNORECASE,
        )
        if m:
            out[key] = _safe_float(m.group(2))
            continue
        for line in lines:
            if any(re.search(p, line, flags=re.IGNORECASE) for p in pats):
                m2 = re.search(NUM_PAT, line)
                if m2:
                    out[key] = _safe_float(m2.group(0))
                break

    return {"values": out, "debug_lines": lines}
