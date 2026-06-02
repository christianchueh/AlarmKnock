# cron_alarm.py
import os
import csv
import requests
from datetime import datetime, timedelta

def main():
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
    GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL") # 👈 鬧鐘也需要這個傳送門網址
    
    if "/edit" in GOOGLE_SHEET_URL:
        csv_url = GOOGLE_SHEET_URL.split("/edit")[0] + "/export?format=csv"
    else:
        csv_url = GOOGLE_SHEET_URL

    response = requests.get(csv_url)
    response.encoding = 'utf-8'
    reader = csv.reader(response.text.splitlines())
    
    # 讀取標頭，確保我們能用欄位名稱對應（順序：title, status, owner, deadline, remind_before, reminded）
    header = next(reader)
    
    now_taiwan = datetime.utcnow() + timedelta(hours=8)
    print(f"🤖 鬧鐘助理巡邏中... 當前台灣時間：{now_taiwan.strftime('%Y-%m-%d %H:%M')}")

    for row in reader:
        # 防呆：確保整行資料是完整的
        if len(row) < 6: continue
        
        title, status, owner, deadline, remind_before, reminded = row[0], row[1], row[2], row[3], row[4], row[5]
        
        # 🎯 雙重防線：只有狀態是 To Do，且 reminded 還是 FALSE 的任務才處理！
        if status.strip() == "To Do" and reminded.strip().upper() == "FALSE":
            try:
                deadline_time = datetime.strptime(deadline.strip(), "%Y-%m-%d %H:%M")
                remind_before_mins = int(remind_before)
            except:
                continue
                
            trigger_time = deadline_time - timedelta(minutes=remind_before_mins)
            
            # 🔍 時間到了！
            if now_taiwan >= trigger_time:
                # 🚀 動作一：發送 Discord
                payload = {
                    "content": f"⏰ **【即將到期提醒】** 任務即將截止！",
                    "embeds": [{
                        "title": f"🔔 任務：{title}",
                        "description": f"👤 負責人：{owner}\n⏳ 截止時間：{deadline}",
                        "color": 15158332
                    }]
                }
                requests.post(DISCORD_WEBHOOK_URL, json=payload)
                print(f"🟢 Discord 通知成功：{title}")
                
                # 📝 動作二：立刻回寫 Google Sheets，把狀態更新為已提醒！
                update_data = {
                    "action": "mark_reminded",
                    "title": title,
                    "owner": owner
                }
                # 呼叫 Apps Script 幫我們在對應的那一列 F 欄填上 TRUE
                requests.post(GOOGLE_SCRIPT_URL, json=update_data)
                print(f"🔒 雲端狀態已鎖定，下次不會再重複發送【{title}】。")

if __name__ == "__main__":
    main()
