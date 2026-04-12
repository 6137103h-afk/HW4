import pandas as pd
import numpy as np
import pingouin as pg
import plotly.express as px
import os
from datetime import datetime
import warnings

# =========================
# 1. 基礎設定與工具
# =========================
DEFAULT_XLSX_PATH = "data_all.xlsx"
RESULTS_DIR = "results"
warnings.filterwarnings("ignore")

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def ensure_dirs():
    """建立產出用的資料夾結構"""
    os.makedirs(f"{RESULTS_DIR}/plots", exist_ok=True)
    os.makedirs(f"{RESULTS_DIR}/stats", exist_ok=True)

# =========================
# 2. 資料前處理 (處理反向題與標題)
# =========================
def preprocess_data(df):
    log("正在清理資料格式與處理反向題...")
    
    # ⭐ 關鍵修正：自動刪除標題前後的所有隱形空白，防止 KeyError
    df.columns = df.columns.str.strip()
    
    # A. 處理學習投入度 (共 26 題，採 1-5 分制)
    # 根據量表：反向題為 5,6,7,8,14,15,16,21,22,23,24,25,26
    eng_reverse = [5, 6, 7, 8, 14, 15, 16, 21, 22, 23, 24, 25, 26]
    for q in eng_reverse:
        col = f'Engage_Post_Q{q}'
        if col in df.columns:
            # 反向計分：1分變5分，5分變1分
            df[col] = 6 - df[col]
    
    # 重新計算投入度平均分 (確保統計結果準確)
    eng_cols = [f'Engage_Post_Q{i}' for i in range(1, 27) if f'Engage_Post_Q{i}' in df.columns]
    if eng_cols:
        df['Engage_Final_Avg'] = df[eng_cols].mean(axis=1)

    # B. 處理認知負荷 (共 7 題，採 1-5 分制)
    clq_cols = [f'CLQ_Post_Q{i}' for i in range(1, 8) if f'CLQ_Post_Q{i}' in df.columns]
    if clq_cols:
        df['CLQ_Final_Avg'] = df[clq_cols].mean(axis=1)
    
    return df

# =========================
# 3. 統計分析邏輯 (ANCOVA, T-Test, ICC)
# =========================
def run_ancova(df, target_name, dv_col, covar_col):
    """執行共變數分析 (ANCOVA) 並繪圖"""
    log(f"執行 {target_name} 的 ANCOVA (排除前測差異)...")
    try:
        # 統計運算
        res = pg.ancova(data=df, dv=dv_col, covar=covar_col, between='Group')
        res.to_csv(f"{RESULTS_DIR}/stats/ancova_{target_name.lower()}.csv")
        print(f"\n--- {target_name} ANCOVA Result ---")
        print(res)
        
        # 視覺化：前後測散佈圖與趨勢線
        fig = px.scatter(df, x=covar_col, y=dv_col, color='Group', trendline='ols',
                         title=f"{target_name} 效果分析 (ANCOVA)",
                         labels={'Group': '組別 (0:對照, 1:實驗)', dv_col: '後測分數', covar_col: '前測分數'})
        fig.write_image(f"{RESULTS_DIR}/plots/ancova_{target_name.lower()}.png")
    except Exception as e:
        log(f"⚠️ {target_name} ANCOVA 執行失敗: {e}")

def run_ttest(df, target_name, dv_col):
    """執行獨立樣本 t 檢定並繪圖"""
    log(f"執行 {target_name} 的組別差異檢定 (t-test)...")
    try:
        # 統計運算
        res = pg.ttest(df[df['Group']==1][dv_col], df[df['Group']==0][dv_col])
        res.to_csv(f"{RESULTS_DIR}/stats/ttest_{target_name.lower()}.csv")
        print(f"\n--- {target_name} t-test Result ---")
        print(res)
        
        # 視覺化：箱型圖與分佈點
        fig = px.box(df, x='Group', y=dv_col, color='Group', points="all",
                    title=f"{target_name} 組別平均值比較",
                    labels={'Group': '組別 (0:對照, 1:實驗)', dv_col: '平均分數'})
        fig.write_image(f"{RESULTS_DIR}/plots/ttest_{target_name.lower()}.png")
    except Exception as e:
        log(f"⚠️ {target_name} t-test 執行失敗: {e}")

def run_icc(df):
    """執行評分者間信度分析 (ICC)"""
    log("執行 CPAM 作品評分者間信度 (ICC)...")
    try:
        # 轉換資料格式以符合 ICC 需求
        icc_df = df[['ID', 'CPAM_Rater_A', 'CPAM_Rater_B']].melt(id_vars='ID', var_name='Rater', value_name='Score')
        res = pg.intraclass_corr(data=icc_df, targets='ID', raters='Rater', ratings='Score').set_index('Type')
        res.to_csv(f"{RESULTS_DIR}/stats/icc_cpam.csv")
        print("\n--- CPAM Inter-rater Reliability (ICC) ---")
        print(res)
    except Exception as e:
        log(f"⚠️ ICC 分析失敗: {e}")

# =========================
# 4. 主執行流程
# =========================
def main():
    ensure_dirs()
    log("🚀 開始執行研究數據分析...")
    
    # 讀取 Excel
    if not os.path.exists(DEFAULT_XLSX_PATH):
        log(f"❌ 找不到檔案: {DEFAULT_XLSX_PATH}，請確認檔案已放在正確資料夾。")
        return

    df = pd.read_excel(DEFAULT_XLSX_PATH)
    
    # 資料前處理 (包含欄位清理)
    df = preprocess_data(df)

    # 第一階段：ANCOVA (分析知識與自我效能，排除起點差異)
    # 分析知識測驗
    run_ancova(df, "Knowledge", "Know_Post", "Know_Pre")
    # 分析程式自我效能 (使用總分)
    run_ancova(df, "CPSES", "CPSES_Post_Total", "CPSES_Pre_Total")

    # 第二階段：t-test (分析認知負荷與學習投入度)
    # 分析認知負荷
    run_ttest(df, "Cognitive_Load", "CLQ_Final_Avg")
    # 分析學習投入程度
    run_ttest(df, "Engagement", "Engage_Final_Avg")

    # 第三階段：信度分析 (CPAM 作品評量)
    run_icc(df)

    log(f"🎉 分析完成！所有結果已儲存至 '{RESULTS_DIR}' 資料夾。")

if __name__ == "__main__":
    main()