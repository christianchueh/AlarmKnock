# cron_alarm.py
import os
import csv
import requests

def main():
    # 🔒 從 GitHub Secrets 抓取環境變數
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
    
    if not GOOGLE_SHEET_URL:
        print("❌ 錯誤：找不到 GOOGLE_SHEET_URL 環境變數")
        return

    # 💡 將您的 Google Sheet 網址後綴轉換為 CSV 下載連結
    # 🎯 關鍵：我們加上 &gid=... 或指定對應的匯出方式，確保讀取到您的 "Tasks" 工作表
    if "/edit" in GOOGLE_SHEET_URL:
        csv_url = GOOGLE_SHEET_URL.split("/edit")[0] + "/export?format=csv"
    else:
        csv_url = GOOGLE_SHEET_URL

    # 下載您雲端上的 Trello 資料
    response = requests.get(csv_url)
    response.encoding = 'utf-8'
    
    # 用 CSV 讀取器解析（這會拿到您表單定義的 title, status, owner 欄位）
    lines = response.text.splitlines()
    reader = csv.DictReader(lines)

    print("🤖 鬧鐘助理醒來了！開始巡邏 Trello 雲端看板...")
    
    has_todo = False

    for row in reader:
        # 確保有讀到您表單的欄位名稱
        if not row.get("title") or not row.get("status"):
            continue
            
        current_status = row["status"].strip()
        
        # 🎯 核心邏輯：如果狀態還是您畫面上設定的 "To Do"
        if current_status == "To Do":
            has_todo = True
            task_title = row["title"]
            task_owner = row.get("owner", "未指派")
            
            # 🚀 組裝發送給 Discord 的提醒卡片
            payload = {
                "content": f"⚠️ **【任務催辦令】** 發現有待辦事項尚未開工！",
                "embeds": [{
                    "title": f"📌 任務：{task_title}",
                    "description": f"👤 **負責人：** <@{task_owner}> (請儘速將狀態移至 In Progress)\n🚦 **目前狀態：** {current_status}",
                    "color": 15158332  # 🔴 紅色代表 To Do 警報
                }]
            }
            
            # 發送 Webhook
            status = requests.post(DISCORD_WEBHOOK_URL, json=payload).status_code
            if status == 204:
                print(f"🟢 【催辦成功】已發送通知：{task_title} (負責人: {task_owner})")
            else:
                print(f"🔴 發送失敗，錯誤碼：{status}")

    if not has_todo:
        print("🏖️ 檢查完畢！目前沒有任何 To Do 任務，大家都很棒！")

if __name__ == "__main__":
    main()
