# pages/1_📝_新增行程.py
import streamlit as st
import pandas as pd
import requests  # 👈 引入最穩定的純 Python 網路傳送工具

st.set_page_config(layout="wide")
st.title("📋 階段四終極完成版：GitHub 雲端同步 Trello 看板")
st.caption("授權標註：edit by 闕河正 | 完整功能版 (Python 3.14 相容修正)")

# 🔒 從祕密抽屜讀取您的 Google Apps Script 傳送門網址與一般網址
GOOGLE_SCRIPT_URL = st.secrets.get("GOOGLE_SCRIPT_URL")
GOOGLE_SHEET_URL = st.secrets.get("GOOGLE_SHEET_URL")

# 📥 【讀取資料】改用網址直接抓取 CSV，徹底跳過 st.connection 罷工問題
if GOOGLE_SHEET_URL:
    csv_url = GOOGLE_SHEET_URL.split("/edit")[0] + "/export?format=csv"
    try:
        df = pd.read_csv(csv_url)
    except Exception:
        df = pd.DataFrame(columns=["title", "status", "owner"])
else:
    df = pd.DataFrame(columns=["title", "status", "owner"])

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
    
    submit_btn = st.form_submit_button("確認指派並同步雲端")

if submit_btn and new_title and new_owner:
    new_data = {"title": new_title, "status": new_status, "owner": new_owner}
    
    # 💡 教授原創的核心安全：新版 Python 拼接表格
    new_row = pd.DataFrame([new_data])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    
    # 🚀 【寫入資料】不用 conn.update，改用純 requests 穿過傳送門打給 Google Sheets
    if GOOGLE_SCRIPT_URL:
        with st.spinner("正在跨越環境限制，同步寫入 Google 試算表..."):
            # 把新任務單獨打包發送
            res = requests.post(GOOGLE_SCRIPT_URL, json=new_data)
            if res.text == "SUCCESS":
                st.success("🎉 資料已跨越限制，成功同步寫入 Google 試算表！")
                st.rerun()
            else:
                st.error("❌ 雲端寫入失敗，請檢查 Apps Script 設定")
    else:
        st.error("❌ 找不到 GOOGLE_SCRIPT_URL 設定！")

st.write("---")

# ==========================================
# 🗂️ 區塊二：下方 Trello 三縱欄畫布與卡片渲染（這段是教授完美的結晶，完全不動！）
# ==========================================
st.write("### 🗂️ 看板動態狀態監控")
trello_col1, trello_col2, trello_col3 = st.columns(3)

# 🔴 【第一欄：To Do】
with trello_col1:
    st.markdown("### <span style='color:red'>🔴 To Do (待辦)</span>", unsafe_allow_html=True)
    todo_list = df[df["status"] == "To Do"]
    if not todo_list.empty:
        for idx, row in todo_list.iterrows():
            with st.container(border=True):
                st.write(f"**📌 {row['title']}**")      
                st.caption(f"負責人: {row['owner']}")   
    else:
        st.info("暫無待辦任務")

# 🟡 【第二欄：In Progress】
with trello_col2:
    st.markdown("### <span style='color:orange'>🟡 In Progress (執行中)</span>", unsafe_allow_html=True)
    ip_list = df[df["status"] == "In Progress"]
    if not ip_list.empty:
        for idx, row in ip_list.iterrows():
            with st.container(border=True):
                st.write(f"**⚡ {row['title']}**")
                st.caption(f"負責人: {row['owner']}")
    else:
        st.info("暫無執行中任務")

# 🟢 【第三欄：Done】
with trello_col3:
    st.markdown("### <span style='color:green'>🟢 Done (已完成)</span>", unsafe_allow_html=True)
    done_list = df[df["status"] == "Done"]
    if not done_list.empty:
        for idx, row in done_list.iterrows():
            with st.container(border=True):
                st.write(f"**✅ {row['title']}**")
                st.caption(f"負責人: {row['owner']}")
    else:
        st.info("暫無已完成任務")
