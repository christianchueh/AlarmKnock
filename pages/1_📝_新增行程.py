# pages/1_📝_新增行程.py
import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout="wide")
st.title("📋 階段四終極完成版：GitHub 雲端同步 Trello 看板")
st.caption("授權標註：edit by 闕河正 | 完整功能版 (精準時間提醒擴充)")

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
        
    # ─── ➕ 闕教授提案：新增時間與提前提醒設定 ───
    c_date, c_time, c_remind = st.columns([1, 1, 2])
    with c_date:
        task_date = st.date_input("📅 截止日期", datetime.date.today())
    with c_time:
        task_time = st.time_input("⏰ 截止時間", datetime.time(12, 0))
    with c_remind:
        remind_mins = st.selectbox("🔔 提前多久提醒我？", [0, 5, 10, 20, 30, 60], format_func=lambda x: "時間到才提醒" if x==0 else f"任務開始前 {x} 分鐘")
    # ──────────────────────────────────────────
    
    submit_btn = st.form_submit_button("確認指派並同步雲端")

if submit_btn and new_title and new_owner:
    # 💡 將日期與時間組合成鬧鐘看得懂的標準格式： YYYY-MM-DD HH:MM
    deadline_str = f"{task_date} {task_time.strftime('%H:%M')}"
    
    # 準備新資料，包含時間與提醒參數
    new_data = {
        "title": new_title, 
        "status": new_status, 
        "owner": new_owner,
        "deadline": deadline_str,        # ➕ 新增：截止時間字串
        "remind_before": int(remind_mins) # ➕ 新增：提前幾分鐘（整數）
    }
    new_row = pd.DataFrame([new_data])
    
    # 表格拼接並上傳
    updated_df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="Tasks", data=updated_df)
    st.success("🎉 任務與提醒時間已成功同步寫入 Google 試算表！")
    st.rerun() 

st.write("---")

# ==========================================
# 🗂️ 區塊二：下方 Trello 看板渲染 (維持原樣，但卡片多顯示時間)
# ==========================================
st.write("### 🗂️ 看板動態狀態監控")
trello_col1, trello_col2, trello_col3 = st.columns(3)

def render_cards(task_df):
    if not task_df.empty:
        for idx, row in task_df.iterrows(): 
            with st.container(border=True):
                st.write(f"**📌 {row['title']}**")      
                st.caption(f"負責人: {row['owner']}")   
                # 💡 貼心調整：如果資料表裡有 deadline 欄位，就顯示在卡片上
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
