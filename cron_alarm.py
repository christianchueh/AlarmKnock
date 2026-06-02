# cron_alarm.py
import os
import csv
import requests
from datetime import datetime, timedelta

def main():
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
    
    if not GOOGLE_SHEET_URL:
        print("❌ 錯誤：找不到 GOOGLE_SHEET_URL")
        return

    if "/edit" in GOOGLE_SHEET_URL:
        csv_url = GOOGLE_SHEET_URL.split("/edit")[0] + "/export?format=csv"
    else:
        csv_url = GOOGLE_SHEET_URL

    response = requests.get(csv_url)
    response.encoding = 'utf-8'
    
    lines = response.text.splitlines()
    reader = csv.DictReader(lines)

    # ⏱️ 獲取當前台灣時間 (UTC + 8)
    now_taiwan = datetime.utcnow() + timedelta(hours=8)
    print(f"🤖 鬧鐘助理巡邏中... 當前台灣時間：{now_taiwan.strftime('%Y-%m-%d %H:%M')}")

    for row in reader:
        if not row.get("title") or not row.get("deadline"):
            continue
            
        current_status = row["status"].strip()
        
        # 🎯 只針對還沒完成的任務 (To Do) 進行時間倒數檢查
        if current_status == "To Do":
            task_title = row["title"]
            task_owner = row.get("owner", "未指派")
            
            # 解析試算表中的截止時間
            try:
                deadline_time = datetime.strptime(row["deadline"].strip(), "%Y-%m-%d %H:%M")
                remind_before_mins = int(row.get("remind_before", 0))
            except Exception as e:
                print(f"⚠️ 任務【{task_title}】時間格式解析錯誤，跳過。")
                continue
            
            # 💡 計算「應該觸發提醒的時間點」：截止時間減去提前的分鐘數
            trigger_time = deadline_time - timedelta(minutes=remind_before_mins)
            
            # 🔍 巡邏核心檢查：如果「現在時間」已經大於等於「應該提醒的時間」
            if now_taiwan >= trigger_time:
                # 為了避免每次排程重複轟炸 Discord，我們可以做個防呆提示
                print(f"🚨 檢查到任務【{task_title}】已達提醒門檻！(設定：提前 {remind_before_mins} 分鐘)")
                
                payload = {
                    "content": f"⏰ **【即將到期提醒】** 負責人請注意進度！",
                    "embeds": [{
                        "title": f"🔔 任務：{task_title}",
                        "description": f"👤 **負責人：** {task_owner}\n⏳ **截止時間：** {row['deadline']}\n🚨 **提醒設定：** 提前 {remind_before_mins} 分鐘通知\n🚦 **目前狀態：** {current_status}",
                        "color": 15158332  # 🔴 紅色
                    }]
                }
                
                requests.post(DISCORD_WEBHOOK_URL, json=payload)
                print(f"🟢 已成功向 Discord 發送【{task_title}】的時間催辦令！")

if __name__ == "__main__":
    main()
