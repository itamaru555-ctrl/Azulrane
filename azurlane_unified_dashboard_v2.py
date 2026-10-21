import math
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ページ基本設定（アズレン風ナビイ・ダークブルーレイアウト）
st.set_page_config(
    page_title="アズレン統合攻略＆経済学最適化ダッシュボード",
    layout="wide",
    page_icon="⚓"
)

# カスタムCSS（高コントラスト・明るい文字色テーマ）
st.markdown("""
    <style>
    /* 全体背景とデフォルト文字色 */
    .stApp {
        background-color: #0b1320 !important;
        color: #ffffff !important;
    }
    
    /* ヘッダー・文字全般を明るい白に強制 */
    h1, h2, h3, h4, h5, h6, p, span, label, div, li, td, th {
        color: #ffffff !important;
    }

    /* フォームのラベル・入力欄 */
    .stNumberInput label, .stSlider label, .stSelectbox label, div[data-widget="stNumberInput"] label {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }
    
    div[data-baseweb="input"], input {
        color: #ffffff !important;
        background-color: #1a273e !important;
    }

    /* メトリック (数字・ラベル) */
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: bold !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }

    /* データフレーム (表) のテキストと背景 */
    [data-testid="stDataFrame"], div[data-testid="stTable"] {
        background-color: #162235 !important;
        color: #ffffff !important;
    }
    
    /* タブのテキスト */
    .stTabs [data-baseweb="tab"] {
        color: #cbd5e1 !important;
        font-size: 1.05rem !important;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        font-weight: bold !important;
        border-bottom-color: #38bdf8 !important;
    }

    /* サブヘッダー・キャプション */
    .stCaption, small {
        color: #94a3b8 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚓ アズレン統合攻略 & ミクロ経済学最適化ダッシュボード")
st.caption("イベントPTの効率的交換計画から、限界分析・ラグランジュ制約最適化までを一元管理する統合シミュレーターなのだ！")

# --- タブ構成 ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🛒 イベントショップ交換計画",
    "🎯 目標資金・周回数算定",
    "⚖️ 制約付き最適化 (ラグランジュ分析)",
    "⚔️ 海域効率比較"
])

# ==========================================
# TAB 1: イベントショップ交換計画
# ==========================================
with tab1:
    st.header("🛒 イベントショップ交換計画")
    st.markdown("デイリー収入と残り日数から、優先度別の目標達成に必要な残り周回数とオイル消費量を算出するのだ！")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.subheader("1. 現在の状況")
        current_pt = st.number_input("現在の所持Pt", value=22330, step=100, key="t1_cur_pt")
        daily_income = st.number_input("1日の収入 (デイリー/SP等)", value=2240, step=100, key="t1_daily_inc")
        remaining_days = st.number_input("イベント残り日数", value=2.0, step=0.5, key="t1_rem_days")

    with col_in2:
        st.subheader("2. 周回効率")
        pt_per_run = st.number_input("1周あたりの獲得Pt", value=180, step=10, key="t1_pt_run")
        oil_per_run = st.number_input("1周あたりの消費燃料", value=267, step=10, key="t1_oil_run")

    st.markdown("---")
    
    # 計算ロジック
    estimated_final_pt = current_pt + (daily_income * remaining_days)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("現在の所持Pt", f"{current_pt:,} Pt")
    with m2:
        st.metric("1日の収入 (周回なし)", f"{daily_income:,} Pt")
    with m3:
        st.metric("1周あたり効率", f"{pt_per_run} Pt / {oil_per_run} 燃料")
    with m4:
        st.metric(
            f"{remaining_days}日後の見込みPt",
            f"{int(estimated_final_pt):,} Pt",
            delta=f"+{int(daily_income * remaining_days):,} Pt"
        )
        
    st.subheader("🎯 アイテム交換順位 & 必要周回数")
    
    # アイテムデータ
    items_data = [
        {"優先": 1, "アイテム": "トラファルガー (2隻目)", "必要Pt": 21750},
        {"優先": 2, "アイテム": "結晶：グロリアス(META) ×4", "必要Pt": 8000},
        {"優先": 3, "アイテム": "特殊装備コア ×5", "必要Pt": 1500},
        {"優先": 4, "アイテム": "特殊装備強化石T1 ×50 (調整枠)", "必要Pt": 4500},
        {"優先": 5, "アイテム": "メンタルユニット ×10 (調整枠)", "必要Pt": 3000},
    ]

    cum_pt = 0
    table_rows = []

    for item in items_data:
        cum_pt += item["必要Pt"]
        needed_from_runs = max(0, cum_pt - estimated_final_pt)

        runs_needed = math.ceil(needed_from_runs / pt_per_run) if pt_per_run > 0 else 0
        runs_per_day = runs_needed / remaining_days if remaining_days > 0 else 0
        oil_needed = runs_needed * oil_per_run

        table_rows.append({
            "優先": item["優先"],
            "アイテム": item["アイテム"],
            "必要Pt": f"{item['必要Pt']:,}",
            "累計必要Pt": f"{cum_pt:,}",
            "残り周回数": f"{runs_needed} 周" if runs_needed > 0 else "0 周 (達成可能)",
            "1日あたり周回": f"{runs_per_day:.1f} 周" if runs_needed > 0 else "-",
            "必要燃料": f"約 {oil_needed:,}" if oil_needed > 0 else "-"
        })

    df_items = pd.DataFrame(table_rows)
    st.dataframe(df_items, use_container_width=True, hide_index=True)
    st.info("💡 **調整枠について**: 目標のPtに届かない場合は、下位の調整枠の交換数を削ることで燃料消費を抑えられます。")

# ==========================================
# TAB 2: 目標資金・周回数算定
# ==========================================
with tab2:
    st.header("🎯 目標ゴールド・周回数算定")
    col_t2_left, col_t2_right = st.columns([1, 2])
    
    with col_t2_left:
        target_gold = st.number_input("目標ゴールド (Gold)", value=1000000, step=50000, key="t2_gold")
        gold_per_run = st.number_input("1周あたり獲得Gold", value=1350, step=50, key="t2_gpr")
        oil_cost_run = st.number_input("1周あたり消費オイル", value=27, step=1, key="t2_ocr")
        clear_time_sec = st.number_input("1周平均クリア時間 (秒)", value=135, step=5, key="t2_cts")
        exp_per_run = st.number_input("1周あたり獲得総EXP", value=1450, step=50, key="t2_epr")

    runs = math.ceil(target_gold / gold_per_run)
    total_oil = runs * oil_cost_run
    total_time_sec = runs * clear_time_sec
    total_exp = runs * exp_per_run

    with col_t2_right:
        st.subheader("📊 算定結果")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("必要周回数", f"{runs:,} 回")
        k2.metric("総消費オイル", f"{total_oil:,} Oil")
        hrs = int(total_time_sec // 3600)
        mins = int((total_time_sec % 3600) // 60)
        k3.metric("総所要時間", f"{hrs}h {mins}m")
        k4.metric("獲得総EXP", f"{total_exp:,} EXP")
        
        # Plotlyグラフ
        run_arr = np.linspace(0, runs, 30)
        df_chart = pd.DataFrame({
            "周回数": run_arr,
            "獲得ゴールド": run_arr * gold_per_run,
            "消費オイル": run_arr * oil_cost_run
        })
        fig = px.line(df_chart, x="周回数", y=["獲得ゴールド", "消費オイル"], 
                      title="リソース累積進行シミュレーション",
                      color_discrete_sequence=["#38bdf8", "#f59e0b"])
        fig.update_layout(paper_bgcolor="#162235", plot_bgcolor="#111b2c", font_color="#ffffff")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 3: 制約付き最適化 (ラグランジュ分析)
# ==========================================
with tab3:
    st.header("⚖️ 制約付き最適化 (ラグランジュの未定乗数法)")
    st.markdown("オイル上限と使える時間の「二重の予算制約線」から、達成可能な最大の周回数と効率限界を算出するのだ！")
    
    c1, c2 = st.columns(2)
    with c1:
        oil_limit = st.slider("所持オイル（予算制約I_oil）", 1000, 30000, 10000, step=1000)
    with c2:
        time_limit_hours = st.slider("使える時間（予算制約I_time [時間]）", 1.0, 10.0, 3.0, step=0.5)

    time_limit_sec = time_limit_hours * 3600
    runs_by_oil = oil_limit / oil_cost_run
    runs_by_time = time_limit_sec / clear_time_sec
    
    max_possible_runs = min(runs_by_oil, runs_by_time)
    bottleneck = "オイル（資金力）" if runs_by_oil < runs_by_time else "プレイ時間"
    
    st.success(f"💡 最適解: 最大周回数は **{int(max_possible_runs):,} 回** (ボトルネック要因: **{bottleneck}**)")
    
    x_oil = np.linspace(10, oil_limit, 50)
    y_time_mins = (x_oil / oil_cost_run) * (clear_time_sec / 60)
    
    df_tradeoff = pd.DataFrame({
        "オイル消費": x_oil,
        "必要時間 (分)": y_time_mins
    })
    fig_tr = px.line(df_tradeoff, x="オイル消費", y="必要時間 (分)", 
                     title="オイル消費 vs 必要時間の限界トレードオフ曲線",
                     color_discrete_sequence=["#10b981"])
    fig_tr.add_vline(x=max_possible_runs * oil_cost_run, line_dash="dash", line_color="#ef4444", annotation_text="最適限界点 (x*)")
    fig_tr.update_layout(paper_bgcolor="#162235", plot_bgcolor="#111b2c", font_color="#ffffff")
    st.plotly_chart(fig_tr, use_container_width=True)

# ==========================================
# TAB 4: 海域効率比較
# ==========================================
with tab4:
    st.header("⚔️ 海域効率比較")
    st.markdown("12-4、13-4、14-4の主要周回海域の限界効果（燃費・タイパ）を比較するのだ！")
    
    maps_data = [
        {"海域": "12-4", "1周Gold": 1100, "消費オイル": 23, "クリア秒": 110, "獲得EXP": 1200},
        {"海域": "13-4", "1周Gold": 1350, "消費オイル": 27, "クリア秒": 135, "獲得EXP": 1450},
        {"海域": "14-4", "1周Gold": 1650, "消費オイル": 33, "クリア秒": 165, "獲得EXP": 1800},
    ]
    df_maps = pd.DataFrame(maps_data)
    df_maps["燃費効率 (Gold/Oil)"] = (df_maps["1周Gold"] / df_maps["消費オイル"]).round(2)
    df_maps["時間効率 (Gold/Sec)"] = (df_maps["1周Gold"] / df_maps["クリア秒"]).round(2)
    df_maps["EXP燃費 (EXP/Oil)"] = (df_maps["獲得EXP"] / df_maps["消費オイル"]).round(2)
    
    st.dataframe(df_maps, use_container_width=True, hide_index=True)
    
    fig_bar = px.bar(df_maps, x="海域", y=["燃費効率 (Gold/Oil)", "時間効率 (Gold/Sec)"],
                     barmode="group", title="海域別限界効率指標の比較",
                     color_discrete_sequence=["#38bdf8", "#f59e0b"])
    fig_bar.update_layout(paper_bgcolor="#162235", plot_bgcolor="#111b2c", font_color="#ffffff")
    st.plotly_chart(fig_bar, use_container_width=True)
