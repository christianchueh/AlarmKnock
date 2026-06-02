# modules/models.py
import requests

class Event:
    def __init__(self, title, details, time_string):
        self.title = title if title.strip() else "📌 未命名行程"
        self.details = details
        self.time_string = time_string

    # 🎯 檢查這裡！前面必須空 4 個空格，確保它在 Class 肚子裡
    def to_dict(self):
        """🧱 核心功能：把自己轉換成適合寫入 Google Sheet 的字典格式"""
        return {
            "title": self.title,
            "details": self.details,
            "time_string": self.time_string
        }

    # 🎯 檢查這裡！一樣空 4 個空格
    def send_to_discord(self, webhook_url):
        if not webhook_url:
            return 400
        payload = {
            "embeds": [{
                "title": self.title,
                "description": f"行程時間：{self.time_string}\n\n備註：{self.details}",
                "color": 3447003
            }]
        }
        response = requests.post(webhook_url, json=payload)
        return response.status_code
