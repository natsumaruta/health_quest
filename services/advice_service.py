# services/advice_service.py
def analyze_values(v: dict) -> dict:
    flags, comments = [], []

    def add(cond, label):
        if cond:
            flags.append(label)

    # --- ピンク系の例 ---
    add(v.get("sbp") is not None and v["sbp"] >= 160, "収縮期血圧≥160")
    add(v.get("dbp") is not None and v["dbp"] >= 100, "拡張期血圧≥100")
    add(v.get("tg") is not None and v["tg"] >= 1000, "中性脂肪≥1000")
    add(v.get("ldl") is not None and v["ldl"] >= 180, "LDL≥180")
    add(v.get("hba1c") is not None and v["hba1c"] >= 6.5, "HbA1c≥6.5")
    add(v.get("egfr") is not None and v["egfr"] <= 44.9, "eGFR≤44.9")
    add(v.get("ua") is not None and (v["ua"] <= 1.4 or v["ua"] >= 8.0), "尿酸≤1.4 or ≥8.0")

    # --- 短文コメント（最小テンプレ） ---
    if v.get("sbp") and v["sbp"] >= 160:
        comments.append("血圧が高めです。塩分は1日6g目標、有酸素運動を週150分程度。")
    if v.get("hba1c") and v["hba1c"] >= 6.5:
        comments.append("血糖コントロールの悪化が疑われます。主食量の見直しと夜間の間食を控えましょう。")
    if v.get("ldl") and v["ldl"] >= 180:
        comments.append("LDLコレステロールが高値です。揚げ物・バターを控え、魚と大豆製品を増やしましょう。")
    if v.get("tg") and v["tg"] >= 1000:
        comments.append("中性脂肪が極めて高値です。受診の上、飲酒・糖質の見直しを。")
    if v.get("egfr") and v["egfr"] <= 44.9:
        comments.append("腎機能低下が示唆されます。水分を適切にとり、NSAIDs長期使用は避けましょう。")

    # LLM整形は後で差し替え；今はそのまま結合
    summary = " ".join(comments) if comments else "特記事項なし。"
    return {"flags": flags, "comments": comments, "summary": summary}
