import traceback
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

from api.rakuten_api import fetch_recipe_categories, fetch_recipe_category_ranking
import openai
import traceback
from bot.openai_handler import generate_keywords


app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/webhook", methods=["POST"])
def webhook():
  signature = request.headers["X-Line-Signature"]
  body = request.get_data(as_text=True)
  
  # print("--------------", flush=True)
  # print(request.headers, flush=True)
  # print(body, flush=True)
  # print("--------------", flush=True)

  try:
    handler.handle(body, signature)
  except InvalidSignatureError:
    print("Invalid signature. Please check your channel access token and channel secret.")
    abort(400)
  except Exception as e:
    print(f"Unexpected error occurred: {e}")  # その他のエラーをキャッチして出力
    abort(500)
  return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
      user_message = event.message.text
      line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"RecipeMateへようこそ！")
            )
    except Exception as e:
        print(f"Error handling message: {e}"
    )


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)