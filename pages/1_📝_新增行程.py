# pages/1_📝_新增行程.py
import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout="wide")
st.title("📋 階段四終極完成版：GitHub 雲端同步 Trello 看板")
st.caption("授權標註：edit by 闕河正 | 完整功能版")

# 🔒 核心安全：讀取 Secrets 中的 Discord 網址
WEBHOOK_URL = st.secrets.get("DISCORD_WEBHOOK_URL")

# 🤝 原生連線：直接跟 Google Sheets 握手
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Tasks", ttl="0")

# ==========================================
# ➕ 區塊一：上方新增任務輸入表單
# ==========================================
st.write("### ➕ 指派新任務")
with st.form("task_input_form", clear_on_submit=True):
    c_title, c_status, c_owner = st.columns([2, 1, 1]) 
    with c_title:
        new_title = st.text_input("📝 任務名稱", placeholder="輸入任務名稱...")
    with c_status:
        new_status = st.selectbox("🚦 狀態", ["To Do", "In Progress", "Done"])
    with c_owner:
        new_owner = st.text_input("👤 負責人", placeholder="誰來負責...")
        
    # ─── ➕ 闕教授提案：增加時間與提前提醒設定 ───
    c_date, c_time, c_remind = st.columns([1, 1, 2])
    with c_date:
        task_date = st.date_input("📅 截止日期", datetime.date.today())
    with c_time:
        task_time = st.time_input("⏰ 截止時間", datetime.time(12, 0))
    with c_remind:
        remind_mins = st.selectbox("🔔 提前多久提醒我？", [0, 15, 30, 60], format_func=lambda x: "時間到才提醒" if x==0 else f"任務截止前 {x} 分鐘")
    # ──────────────────────────────────────────
    
    submit_btn = st.form_submit_button("確認指派並同步雲端")

if submit_btn and new_title and new_owner:
    # 組合成鬧鐘看得懂的標準時間格式字串： YYYY-MM-DD HH:MM
    deadline_str = f"{task_date} {task_time.strftime('%H:%M')}"
    
    # 🎯 把時間與防重複的標記，順便包進這筆資料裡
    new_data = {
        "title": new_title, 
        "status": new_status, 
        "owner": new_owner,
        "deadline": deadline_str,        # ➕ 新增欄位
        "remind_before": int(remind_mins),# ➕ 新增欄位
        "reminded": "FALSE"               # ➕ 新增防爆欄位（預設未提醒）
    }
    
    # 💡 闕教授原創核心：用 pd.concat() 進行表格拼接
    new_row = pd.DataFrame([new_data])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    
    # 🚀 直接利用套件更新雲端試算表
    conn.update(worksheet="Tasks", data=updated_df)
    st.success("🎉 任務與提醒時間已成功同步寫入 Google 試算表！")
    st.rerun() 

st.write("---")

# ==========================================
# 🗂️ 區塊二：下方 Trello 看板渲染 (完全保留您的精髓)
# ==========================================
st.write("### 🗂️ 看板動態狀態監控")
trello_col1, trello_col2, trello_col3 = st.columns(3)

def render_cards(task_df):
    if not task_df.empty:
        for idx, row in task_df.iterrows(): 
            with st.container(border=True):
                st.write(f"**📌 {row['title']}**")      
                st.caption(f"負責人: {row['owner']}")   
                if "deadline" in row and pd.notna(row["deadline"]):
                    st.caption(f"⏳ 截止: {row['deadline']} (提前 {row.get('remind_before', 0)} 分)")
    else:
        st.info("暫無任務")

with trello_col1:
    st.markdown("### <span style='color:red'>🔴 To Do (待辦)</span>", unsafe_allow_html=True)
    render_cards(df[df["status"] == "To Do"])

with trello_col2:
    st.markdown("### <span style='color:orange'>🟡 In Progress (執行中)</span>", unsafe_allow_html=True)
    render_cards(df[df["status"] == "In Progress"])

with trello_col3:
    st.markdown("### <span style='color:green'>🟢 Done (已完成)</span>", unsafe_allow_html=True)
    render_cards(df[df["status"] == "Done"])
