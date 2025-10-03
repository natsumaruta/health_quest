# services/date_utils.py
import re
from datetime import datetime

# 西暦: 2025/9/30, 2025-09-30, 2025年9月30日
SEIREKI = r"(?P<y>\d{4})[./\-年](?P<m>\d{1,2})[./\-月](?P<d>\d{1,2})日?"

# 簡易 令和: R7/9/30, 令和7年9月30日（必要十分の簡易対応）
WAREKI_R = r"(?:R|令和)(?P<ry>\d{1,2})[./\-年](?P<m>\d{1,2})[./\-月](?P<d>\d{1,2})日?"


def _wareki_to_seireki(ry: str) -> int:
    # 令和1年=2019
    return 2018 + int(ry)


def extract_dates(text: str):
    """OCR文字列からdatetimeのリストを返す（重複除去・昇順）"""
    ds = []

    for m in re.finditer(SEIREKI, text):
        y = int(m.group("y"))
        m_ = int(m.group("m"))
        d_ = int(m.group("d"))
        try:
            ds.append(datetime(y, m_, d_))
        except ValueError:
            pass

    for m in re.finditer(WAREKI_R, text, flags=re.IGNORECASE):
        y = _wareki_to_seireki(m.group("ry"))
        m_ = int(m.group("m"))
        d_ = int(m.group("d"))
        try:
            ds.append(datetime(y, m_, d_))
        except ValueError:
            pass

    # フィルタ（過去/未来のゴミ取り。必要に応じて調整）
    now_y = datetime.now().year
    ds = [dt for dt in ds if 2000 <= dt.year <= now_y + 1]

    # 重複除去して昇順
    uniq = sorted(set(ds))
    return uniq
