import traceback
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, PostbackEvent
import os

from api.rakuten_api import fetch_recipe_categories, fetch_recipe_category_ranking
import openai
import traceback
from bot.openai_handler import generate_keywords
from template.carousel_template import create_carousel_template


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
    try:
      user_message = event.message.text
      keywords = generate_keywords(user_message)

      line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"{keywords}")
      )

      # 何かしらをトリガーとして以下のコードを実行する（レシピを取得する）。

      # # ユーザが入力したカテゴリを取得
      # df_keyword = fetch_recipe_categories(keywords)
      # # print(df_keyword, flush=True)

      # # カテゴリ内のレシピトップ4を取得
      # df_recipe = fetch_recipe_category_ranking(df_keyword)
      # # print(df_recipe, flush=True)
      
      # # カルーセルテンプレートの作成
      # carousel_template = create_carousel_template(df_recipe)

      # line_bot_api.reply_message(
      #   event.reply_token,
      #   TemplateSendMessage(
      #     alt_text="トップ4のレシピ",
      #     template=carousel_template
      #   )
      # )

    except Exception as e:
      print(f"Error handling message: {e}")
      traceback.format_exc()

# お気に入り登録ボタンを押したとき
@handler.add(PostbackEvent)
def on_postback(event):
  # レシピタイトル、レシピURL、画像URLを取得
  data = event.postback.data
  recipe_title, recipe_url, food_image_url = data.split("|")
  
  # あけぴさん、DBに保存する処理をここに書く

  # DBに登録後、メッセージをLINEに表示する
  line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=f'「{recipe_title}」をお気に入り登録しました！')
  )

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)