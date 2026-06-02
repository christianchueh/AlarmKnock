# cron_alarm.py (防當機網頁直改版)
import os
import csv
import requests
from datetime import datetime, timedelta

def main():
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
    
    print("📢 【系統回報】開始下載 Google 試算表...")
    
    if not GOOGLE_SHEET_URL:
        print("❌ 錯誤：密鑰環境變數 GOOGLE_SHEET_URL 是空的！請檢查 GitHub Secrets！")
        return

    if "/edit" in GOOGLE_SHEET_URL:
        csv_url = GOOGLE_SHEET_URL.split("/edit")[0] + "/export?format=csv"
    else:
        csv_url = GOOGLE_SHEET_URL

    try:
        response = requests.get(csv_url, timeout=10)
        response.encoding = 'utf-8'
        all_lines = list(csv.reader(response.text.splitlines()))
    except Exception as e:
        print(f"❌ 錯誤：連線到 Google 試算表大失敗！原因：{e}")
        return

    # 🎯 終極防線：檢查抓下來的到底是不是空表
    if len(all_lines) == 0:
        print("❌ 錯誤：抓下來的試算表內容完全是空的！請確認 GOOGLE_SHEET_URL 的權限是否開啟『知道連結的使用者皆可檢視』！")
        print(f"原始抓取文字前100字：{response.text[:100]}")
        return

    print(f"📊 成功下載！這張表總共有 {len(all_lines)} 行資料（含標頭）。")
    
    now_taiwan = datetime.utcnow() + timedelta(hours=8)
    print(f"🤖 鬧鐘助理巡邏中... 當前台灣時間：{now_taiwan.strftime('%Y-%m-%d %H:%M')}")
    print("🖕 機車咧!!有沒有過！")

    data_rows = all_lines[1:] # 切出實體資料

    for index, row in enumerate(data_rows, start=2):
        print(f"📋 正在檢查第 {index} 橫列資料：{row}")
        if len(row) < 5: 
            print(" 欄位不足 5 個，跳過！")
            continue
        
        title, status, owner, deadline, remind_before = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip()
        
        if status == "To Do":
            try:
                clean_deadline = deadline.replace("/", "-")
                deadline_time = datetime.strptime(clean_deadline, "%Y-%m-%d %H:%M")
                remind_before_mins = int(remind_before)
            except Exception as e:
                print(f"   ❌ 任務【{title}】時間解析失敗，錯誤原因：{e}")
                continue
                
            trigger_time = deadline_time - timedelta(minutes=remind_before_mins)
            print(f"   ⏱️ 預計提醒點：{trigger_time.strftime('%H:%M')} | 目前時間：{now_taiwan.strftime('%H:%M')}")
            
            if trigger_time <= now_taiwan < (trigger_time + timedelta(minutes=60)):
                payload = {
                    "content": f"⏰ **【即將到期提醒】** 任務即將截止！",
                    "embeds": [{
                        "title": f"🔔 任務：{title}",
                        "description": f"👤 **負責人：** {owner}\n⏳ **截止時間：** {deadline}",
                        "color": 15158332
                    }]
                }
                res = requests.post(DISCORD_WEBHOOK_URL, json=payload)
                print(f"   🟢 Discord 通知成功！狀態碼：{res.status_code}")
            else:
                print(f"   🛑 判定：未落入 60 分鐘提醒區間。")
        else:
            print(f"   🛑 判定：狀態不是 To Do (當前是 {status})，略過。")

if __name__ == "__main__":
    main()
