# cron_alarm.py
import os
import csv
from datetime import datetime, timedelta
import requests
# 🎯 重複使用物件工廠
from modules.models import Event

def main():
    # 🔒 從 GitHub Secrets 抓取資料
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
    
    if not GOOGLE_SHEET_URL:
        print("❌ 錯誤：找不到 GOOGLE_SHEET_URL 環境變數")
        return

    # 💡 魔法步驟：將原本的 Google Sheet 網址後面改成 /export?format=csv
    # 這樣 Python 就可以直接把它當成一個線上的 CSV 檔案下載並讀取！
    if "/edit" in GOOGLE_SHEET_URL:
        csv_url = GOOGLE_SHEET_URL.split("/edit")[0] + "/export?format=csv"
    else:
        csv_url = GOOGLE_SHEET_URL

    # 下載 Google Sheet 資料
    response = requests.get(csv_url)
    response.encoding = 'utf-8'
    
    # 解析 CSV
    lines = response.text.splitlines()
    reader = csv.DictReader(lines)

    # 取得現在的台灣時間
    now_taiwan = datetime.utcnow() + timedelta(hours=8)
    print(f"🤖 鬧鐘助理醒來了！目前台灣時間：{now_taiwan.strftime('%Y-%m-%d %H:%M')}")

    for row in reader:
        # 檢查是否欄位齊全
        if not row.get("title") or not row.get("raw_datetime"):
            continue
            
        reminded_status = str(row.get("reminded", "FALSE")).upper()
        
        # 如果這筆行程「還沒通知過」
        if reminded_status == "FALSE":
            event_time = datetime.strptime(row["raw_datetime"], "%Y-%m-%d %H:%M")
            
            # 如果時間到了或過了，就該發通知了！
            if now_taiwan >= event_time:
                # 🏭 呼叫工廠：把 Google Sheet 撈出來的字變回 Event 物件
                ev_obj = Event(row["title"], row["details"], row["time_string"])
                
                # 🚀 物件自我發送！
                status = ev_obj.send_to_discord(DISCORD_WEBHOOK_URL)
                if status == 204:
                    print(f"🟢 【自動通知成功】已發送：{ev_obj.title}")
                    # 💡 備註：因為 CSV 下載是唯讀的，如果要回寫 Google Sheet 狀態需要開 API 權限
                    # 這裡先引導學生：讓 Actions 負責發送，學生手動去 Google Sheet 把 FALSE 改成 TRUE 即可！
                else:
                    print(f"🔴 發送失敗，錯誤碼：{status}")

if __name__ == "__main__":
    main()
