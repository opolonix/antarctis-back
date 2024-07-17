from config import BOT_TOKEN
import requests

def send_message(chat_id: int | str, text: str, button_text: str = None, button_url: str = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if button_text:
        payload['reply_markup'] = {
            "inline_keyboard": [
                [{"text": button_text, "url": button_url}]
            ]
        }
    response = requests.post(url, json=payload)
    return response