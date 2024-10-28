from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
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
    user_message = event.message.text
    print(f"Received LINE message: {user_message}")  # 受信メッセージを出力

    # OpenAI APIにリクエストを送信
    try:
        keywords = generate_keywords(user_message)
        print(f"Generated keywords: {keywords}")
        reply_text = f"楽天Recipe APIのキーワード: {keywords}"
    except Exception as e:
        print(f"Error handling message: {e}", flush=True)
        traceback.print_exc()
        reply_text = "エラーです。"

    # LINEに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)