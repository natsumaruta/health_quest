# services/ocr_post.py
import re
from datetime import datetime

DATE_PATS = [
    r"(?P<y>\d{4})[./年](?P<m>\d{1,2})[./月](?P<d>\d{1,2})日?",  # 2025/9/30, 2025年9月30日
    r"R(?P<ry>\d{1,2})[./年](?P<m>\d{1,2})[./月](?P<d>\d{1,2})日?",  # 令和表記(簡易) R7/9/30
]


# 日付パーサ（日本語表記対応）
def _wareki_to_seireki(ry):  # R=2019
    return 2018 + int(ry)


def extract_dates(text: str):
    dates = []
    for pat in DATE_PATS:
        for m in re.finditer(pat, text):
            y = (
                int(m.group("y"))
                if "y" in m.groupdict() and m.group("y")
                else _wareki_to_seireki(m.group("ry"))
            )
            dt = datetime(y, int(m.group("m")), int(m.group("d")))
            dates.append(dt)
    return sorted(set(dates))


#  対象年の決定 & 年フィルタ
def choose_target_year(lines: list[str]) -> int | None:
    text = "\n".join(lines)
    ds = extract_dates(text)
    return ds[-1].year if ds else None


def filter_lines_by_year(lines: list[str], year: int) -> list[str]:
    # その年の明示や直近近傍を優先（2行以内に日付or年がある行を採用）
    year_pat = re.compile(rf"\b{year}\b|{year}年")
    date_pat = re.compile(rf"{year}[./年]\d{{1,2}}[./月]\d{{1,2}}日?")
    kept = []
    for i, ln in enumerate(lines):
        window = "\n".join(lines[max(0, i - 2) : i + 3])
        if year_pat.search(window) or date_pat.search(window):
            kept.append(ln)
    # 何も残らなければ全行返す（フォールバック）
    return kept or lines
