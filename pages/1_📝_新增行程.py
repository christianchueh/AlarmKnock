import streamlit as st
import requests

# ==========================================
# 核心功能模組：負責專門寄信給 Discord
# ==========================================
def send_discord_webhook(webhook_url, title, content):
    payload = {
        "content": "📢 **【模組化訊息】來自新增行程頁面！**",
        "embeds": [
            {
                "title": f"🚀 {title}",
                "description": content,
                "color": 5763719,  # 綠色
                "footer": {"text": "由 1_新增行程.py 模組獨立執行"}
            }
        ]
    }
    response = requests.post(webhook_url, json=payload)
    return response.status_code

# ==========================================
# 介面設計
# ==========================================
st.title("📝 新增行事曆行程")
st.write("這個畫面的程式碼是完全獨立的，專注處理『輸入資料』與『發送』。")

# 讀取我們存在祕密抽屉裡的網址
WEBHOOK_URL = st.secrets.get("DISCORD_WEBHOOK_URL")

# 輸入框
input_title = st.text_input("請輸入行程名稱：", value="上 闕教授 的 Python 課")
input_content = st.text_area("請輸入行程備註：", value="今天學習了如何將 Streamlit 專案檔案進行模組化切分！")

st.divider()

# 按鈕觸發
if st.button("🚀 確定排入行程並通知 Discord"):
    if not WEBHOOK_URL:
        st.error("❌ 找不到 Webhook 網址，請檢查 Secrets 設定。")
    else:
        with st.spinner("正在呼叫 Discord Webhook 模組..."):
            status = send_discord_webhook(WEBHOOK_URL, input_title, input_content)
            if status == 204:
                st.success("🟢 【模組執行成功】訊息已順利送達 Discord！")
            else:
                st.error(f"🔴 發送失敗，錯誤代碼：{status}")
