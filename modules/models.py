import requests

class Event:
    def __init__(self, title, details, time_string):
        self.title = title
        self.details = details
        self.time_string = time_string

    def send_to_discord(self, webhook_url):
        if not webhook_url:
            return 400
        payload = {
            "embeds": [{
                "title": self.title,
                "description": f"行程時間：{self.time_string}\n\n備註：{self.details}",
                "color": 3447003  # 藍色卡片邊條
            }]
        }
        response = requests.post(webhook_url, json=payload)
        return response.status_code
