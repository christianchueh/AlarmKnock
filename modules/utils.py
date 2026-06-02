def clean_content(title, details):
    safe_title = title if title.strip() else "📌 未命名行程"
    safe_details = details[:50] + "..." if len(details) > 50 else details
    return safe_title, safe_details

def format_time(date_val, time_val):
    return f"📅 {date_val.strftime('%Y/%m/%d')} ⏰ {time_val.strftime('%H:%M')}"
