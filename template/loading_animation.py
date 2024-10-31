import json
import os
import requests

def start_loading_animation(user_id):
  # ローディングアニメーション
  url_loading = "https://api.line.me/v2/bot/chat/loading/start"
  headers_loading = {
    "Content-Type": "application/json",
    "Authorization": f'Bearer {os.getenv("LINE_CHANNEL_ACCESS_TOKEN")}'
  }
  payload_loading = {
    "chatId": user_id,
    "loadingSeconds": 20
  }
  response = requests.post(url_loading, headers=headers_loading, data=json.dumps(payload_loading)) 