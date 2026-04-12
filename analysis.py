import os
import warnings
from datetime import datetime

import pandas as pd
import pingouin as pg
import plotly.express as px

# =========================
# 1. 基礎設定
# =========================
DEFAULT_XLSX_PATH = "data_all.xlsx"
RESULTS_DIR = "results"

warnings.filterwarnings("ignore")


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def ensure_dirs():
    """建立結果輸出資料夾"""
    os.makedirs(os.path.join(RESULTS_DIR, "plots"), exist_ok=True)
    os.makedirs(os.path.join(RESULTS_DIR, "stats"), exist_ok=True)


# =========================
# 2. 資料前處理
# =========================
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    log("正在清理資料格式...")

    # 去除欄位名稱前後空白
    df.columns = df.columns.str.strip()

    # 統一 Group 欄位為 0/1
    # 0 = Control, 1 = Experimental
    if "Group" not in df.columns:
        raise ValueError("找不到 'Group' 欄位。")

    group_map = {
        "Ctrl": 0,
        "Control": 0,
        "CG": 0,
        "0": 0,
        0: 0,
        "Exp": 1,
        "Experimental": 1,
        "EG": 1,
        "1": 1,
        1: 1,
    }

    df["Group"] = df["Group"].map(group_map).fillna(df["Group"])

    # 若 Group 還是不是 0/1，報錯
    valid_groups = set(df["Group"].dropna().unique())
    if not valid_groups.issubset({0, 1}):
        raise ValueError(
            f"Group 欄位格式不正確，偵測到的值為: {sorted(valid_groups)}。"
            "請使用 Exp/Ctrl 或 1/0。"
        )

    # 需要的欄位
    required_cols = [
        "ID",
        "Group",
        "CELF5_Pre", "CELF5_Post",
        "STEAM_Pre", "STEAM_Post",
        "IMMS_Pre", "IMMS_Post",
        "CPAM_Post",
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必要欄位: {missing_cols}")

    # 轉成數值
    numeric_cols = [
        "CELF5_Pre", "CELF5_Post",
        "STEAM_Pre", "STEAM_Post",
        "IMMS_Pre", "IMMS_Post",
        "CPAM_Post",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 刪除必要欄位有缺值的列
    before_rows = len(df)
    df = df.dropna(subset=required_cols).copy()
    after_rows = len(df)

    if before_rows != after_rows:
        log(f"已刪除 {before_rows - after_rows} 筆缺漏資料。")

    # 範圍檢查
    validate_score_range(df, "CELF5_Pre", 0, 10)
    validate_score_range(df, "CELF5_Post", 0, 10)
    validate_score_range(df, "STEAM_Pre", 0, 10)
    validate_score_range(df, "STEAM_Post", 0, 10)
    validate_score_range(df, "IMMS_Pre", 0, 50)
    validate_score_range(df, "IMMS_Post", 0, 50)
    validate_score_range(df, "CPAM_Post", 0, 45)

    log(f"資料清理完成，可分析樣本數: {len(df)}")
    return df


def validate_score_range(df: pd.DataFrame, col: str, min_val: float, max_val: float):
    """檢查分數是否超出合理範圍"""
    bad_mask = (df[col] < min_val) | (df[col] > max_val)
    if bad_mask.any():
        bad_count = int(bad_mask.sum())
        raise ValueError(
            f"欄位 '{col}' 有 {bad_count} 筆資料超出範圍 [{min_val}, {max_val}]。"
        )


# =========================
# 3. 描述統計
# =========================
def save_descriptive_stats(df: pd.DataFrame):
    log("輸出描述統計...")

    group_labels = {0: "Control", 1: "Experimental"}
    df_desc = df.copy()
    df_desc["Group_Label"] = df_desc["Group"].map(group_labels)

    cols = [
        "CELF5_Pre", "CELF5_Post",
        "STEAM_Pre", "STEAM_Post",
        "IMMS_Pre", "IMMS_Post",
        "CPAM_Post",
    ]

    desc = df_desc.groupby("Group_Label")[cols].agg(["mean", "std", "min", "max", "count"])
    desc.to_csv(os.path.join(RESULTS_DIR, "stats", "descriptive_statistics.csv"), encoding="utf-8-sig")

    print("\n--- Descriptive Statistics ---")
    print(desc)


# =========================
# 4. ANCOVA
# =========================
def run_ancova(df: pd.DataFrame, target_name: str, dv_col: str, covar_col: str):
    log(f"執行 {target_name} 的 ANCOVA...")
    try:
        res = pg.ancova(
            data=df,
            dv=dv_col,
            covar=covar_col,
            between="Group"
        )

        output_path = os.path.join(RESULTS_DIR, "stats", f"ancova_{target_name.lower()}.csv")
        res.to_csv(output_path, index=False, encoding="utf-8-sig")

        print(f"\n--- {target_name} ANCOVA Result ---")
        print(res)

        # 繪圖
        fig = px.scatter(
            df,
            x=covar_col,
            y=dv_col,
            color=df["Group"].map({0: "Control", 1: "Experimental"}),
            trendline="ols",
            title=f"{target_name} ANCOVA",
            labels={
                covar_col: f"{target_name} Pre-test",
                dv_col: f"{target_name} Post-test",
                "color": "Group",
            },
        )
        fig.write_html(os.path.join(RESULTS_DIR, "plots", f"ancova_{target_name.lower()}.html"))

        # 若環境有 kaleido，順便輸出 png
        try:
            fig.write_image(os.path.join(RESULTS_DIR, "plots", f"ancova_{target_name.lower()}.png"))
        except Exception:
            log(f"{target_name} 圖已輸出 HTML；PNG 未輸出（若需要可安裝 kaleido）。")

    except Exception as e:
        log(f"⚠️ {target_name} ANCOVA 執行失敗: {e}")


# =========================
# 5. t-test
# =========================
def run_ttest(df: pd.DataFrame, target_name: str, dv_col: str):
    log(f"執行 {target_name} 的獨立樣本 t 檢定...")
    try:
        exp_scores = df[df["Group"] == 1][dv_col]
        ctrl_scores = df[df["Group"] == 0][dv_col]

        res = pg.ttest(exp_scores, ctrl_scores, correction="auto")
        output_path = os.path.join(RESULTS_DIR, "stats", f"ttest_{target_name.lower()}.csv")
        res.to_csv(output_path, index=False, encoding="utf-8-sig")

        print(f"\n--- {target_name} t-test Result ---")
        print(res)

        # 繪圖
        fig = px.box(
            df.assign(Group_Label=df["Group"].map({0: "Control", 1: "Experimental"})),
            x="Group_Label",
            y=dv_col,
            color="Group_Label",
            points="all",
            title=f"{target_name} Group Comparison",
            labels={
                "Group_Label": "Group",
                dv_col: target_name,
            },
        )
        fig.write_html(os.path.join(RESULTS_DIR, "plots", f"ttest_{target_name.lower()}.html"))

        try:
            fig.write_image(os.path.join(RESULTS_DIR, "plots", f"ttest_{target_name.lower()}.png"))
        except Exception:
            log(f"{target_name} 圖已輸出 HTML；PNG 未輸出（若需要可安裝 kaleido）。")

    except Exception as e:
        log(f"⚠️ {target_name} t-test 執行失敗: {e}")


# =========================
# 6. 整理摘要表
# =========================
def build_summary_table(df: pd.DataFrame):
    log("整理分析摘要表...")

    summary_rows = []

    analyses = [
        ("CELF5", "ANCOVA", "CELF5_Post", "CELF5_Pre"),
        ("STEAM", "ANCOVA", "STEAM_Post", "STEAM_Pre"),
        ("IMMS", "ANCOVA", "IMMS_Post", "IMMS_Pre"),
        ("CPAM", "TTEST", "CPAM_Post", None),
    ]

    for name, method, dv, covar in analyses:
        try:
            if method == "ANCOVA":
                res = pg.ancova(data=df, dv=dv, covar=covar, between="Group")
                group_row = res[res["Source"] == "Group"].iloc[0]

                summary_rows.append({
                    "Measure": name,
                    "Method": "ANCOVA",
                    "Statistic": "F",
                    "Value": round(float(group_row["F"]), 3),
                    "p-value": round(float(group_row["p-unc"]), 4),
                    "Effect_Size": round(float(group_row["np2"]), 4) if "np2" in group_row else None
                })

            elif method == "TTEST":
                exp_scores = df[df["Group"] == 1][dv]
                ctrl_scores = df[df["Group"] == 0][dv]
                res = pg.ttest(exp_scores, ctrl_scores, correction="auto").iloc[0]

                summary_rows.append({
                    "Measure": name,
                    "Method": "Independent t-test",
                    "Statistic": "t",
                    "Value": round(float(res["T"]), 3),
                    "p-value": round(float(res["p-val"]), 4),
                    "Effect_Size": round(float(res["cohen-d"]), 4)
                })

        except Exception as e:
            summary_rows.append({
                "Measure": name,
                "Method": method,
                "Statistic": "ERROR",
                "Value": str(e),
                "p-value": None,
                "Effect_Size": None
            })

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(
        os.path.join(RESULTS_DIR, "stats", "analysis_summary.csv"),
        index=False,
        encoding="utf-8-sig"
    )

    print("\n--- Analysis Summary ---")
    print(summary_df)


# =========================
# 7. 主程式
# =========================
def main():
    ensure_dirs()
    log("🚀 開始執行研究數據分析...")

    if not os.path.exists(DEFAULT_XLSX_PATH):
        log(f"❌ 找不到檔案: {DEFAULT_XLSX_PATH}")
        log("請把 Excel 檔放在同一個資料夾，並命名為 data_all.xlsx")
        return

    df = pd.read_excel(DEFAULT_XLSX_PATH)
    df = preprocess_data(df)

    save_descriptive_stats(df)

    # ANCOVA
    run_ancova(df, "CELF5", "CELF5_Post", "CELF5_Pre")
    run_ancova(df, "STEAM", "STEAM_Post", "STEAM_Pre")
    run_ancova(df, "IMMS", "IMMS_Post", "IMMS_Pre")

    # t-test
    run_ttest(df, "CPAM", "CPAM_Post")

    # 摘要表
    build_summary_table(df)

    log(f"🎉 分析完成！所有結果已儲存至 '{RESULTS_DIR}' 資料夾。")


if __name__ == "__main__":
    main()
