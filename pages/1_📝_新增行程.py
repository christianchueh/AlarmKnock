import streamlit as st
import datetime

# 🎯 核心精髓：把剛剛寫好的功能積木與物件工廠全部 import 進來！
from modules.utils import clean_content, format_time
from modules.models import Event

st.title("📝 新增行事曆行程")
st.write("這個畫面負責收集資料，並使用我們做好的模組來生產行程。")

# 🔒 安全機制：從 Streamlit 祕密抽屜讀取 Discord 網址
WEBHOOK_URL = st.secrets.get("DISCORD_WEBHOOK_URL")

# 1. 初始化一個箱子 (List)，用來在網頁記憶體中存放所有的行程物件
if "events_list" not in st.session_state:
    st.session_state.events_list = []

# 2. 收集使用者輸入的資料
title_input = st.text_input("輸入行程名稱：")
details_input = st.text_area("輸入詳細備註：")

col1, col2 = st.columns(2)
with col1:
    date_input = st.date_input("日期：", datetime.date.today())
with col2:
    time_input = st.time_input("時間：", datetime.time(12, 0))

st.divider()

# 3. 按了按鈕 ➔ 呼叫工廠 ➔ 生產物件 ➔ 裝箱
if st.button("🧱 生產行程物件並存入清單"):
    # 🧱 使用功能積木一：格式化時間字串
    pretty_time = format_time(date_input, time_input)
    # 🧱 使用功能積木二：清理與過濾文字長度
    safe_title, safe_details = clean_content(title_input, details_input)
    
    # 🏭 使用物件工廠：正式實例化一個 Event 物件
    new_event = Event(safe_title, safe_details, pretty_time)
    
    # 📦 裝箱：把物件丟進清單
    st.session_state.events_list.append(new_event)
    st.success(f"✅ 成功生產一個行程物件：【{new_event.title}】！")

st.divider()

# 4. 把箱子裡的所有物件全部撈出來，並讓它們「自己發送通知」
st.markdown(f"### 📋 目前清單中的行程物件 (共 {len(st.session_state.events_list)} 個)")

for index, ev in enumerate(st.session_state.events_list):
    with st.expander(f"{index + 1}. {ev.title}"):
        st.write(f"**⏰ 預定時間：** {ev.time_string}")
        st.write(f"**📝 詳細備註：** {ev.details}")
        
        # 🎯 每個物件身上都有一顆獨立按鈕，會呼叫自己的 method 把自己發射出去
        if st.button("🚀 叫這個物件自己發送 Discord", key=f"btn_{index}"):
            with st.spinner("物件正在進行自我投遞..."):
                status = ev.send_to_discord(WEBHOOK_URL)
                if status == 204:
                    st.success("🟢 物件自我發送成功！快去 Discord 看看！")
                else:
                    st.error(f"🔴 發送失敗，請檢查環境變數。錯誤碼：{status}")
