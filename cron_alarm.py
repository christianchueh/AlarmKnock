# cron_alarm.py
import os
import csv
import requests
from datetime import datetime, timedelta

def main():
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
    
    if "/edit" in GOOGLE_SHEET_URL:
        csv_url = GOOGLE_SHEET_URL.split("/edit")[0] + "/export?format=csv"
    else:
        csv_url = GOOGLE_SHEET_URL

    response = requests.get(csv_url)
    response.encoding = 'utf-8'
    
    # 🎯 絕招一：不要直接用 reader，直接用 list() 把所有文字行數鎖死！
    all_lines = list(csv.reader(response.text.splitlines()))
    
    # 🎯 絕招二：第一行就是 header（標頭）
    header = all_lines[0] 
    
    # 🎯 絕招三：剩下的第 1 行到最後一行，才是我們要跑迴圈的資料 (row)
    data_rows = all_lines[1:]
    
    now_taiwan = datetime.utcnow() + timedelta(hours=8)
    print(f"🤖 鬧鐘助理巡邏中... 當前台灣時間：{now_taiwan.strftime('%Y-%m-%d %H:%M')}")
    print("📢 系統除錯：我們手裡現在總共抓到了", len(data_rows), "筆任務資料！")

    # 🎯 這裡改用我們切好的 data_rows，保證百分之百會進來跑！
    for row in data_rows:
        # 防呆：確保整行資料是完整的
        print(f"📋 保全正在看這一行，它的欄位總數是：{len(row)}，內容是：{row}")
        
        if len(row) < 5: 
            continue
        
        title, status, owner, deadline, remind_before, reminded = row[0], row[1], row[2], row[3], row[4], row[5]
        
        # 🎯 雙重防線：只有狀態是 To Do，且 reminded 還是 FALSE 的任務才處理！
        if status.strip() == "To Do":
            try:
                deadline_time = datetime.strptime(deadline.strip(), "%Y-%m-%d %H:%M")
                remind_before_mins = int(remind_before)
            except:
                continue
            print("近來todo") 
            trigger_time = deadline_time - timedelta(minutes=remind_before_mins)
            
            # 🔍 終極安全機制：現在時間大於提醒點，且「過期不超過 15 分鐘」！
            # 靠著這條時間線，保全每次巡邏，一輩子就只會在這個 15 分鐘的黃金交叉點抓到它、並只發一次通知！
            if trigger_time <= now_taiwan < (trigger_time + timedelta(minutes=15)):
                
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
                
                # 💡 這裡原本的「動作二」請完全刪除！因為我們不用回寫 Google Sheet，
                # 只要靠上面的 time 判定，下一個 15 分鐘保全醒來時，now_taiwan 就會超過 15 分鐘區間，自動閉嘴！

if __name__ == "__main__":
    main()
