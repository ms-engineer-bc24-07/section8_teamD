import traceback
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, PostbackEvent, ButtonsTemplate, PostbackAction
import os

from api.rakuten_api import NoRecipeFoundError, fetch_recipe_categories, fetch_recipe_category_ranking
import openai
import traceback
from bot.openai_handler import generate_keywords
from template.carousel_template import create_carousel_template
from template.button_template import create_button_template
import pandas as pd



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
        keywords_list = generate_keywords(user_message)

        # キーワードが見つからない場合の処理
        if not keywords_list:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="該当するキーワードが見つかりませんでした。")
            )
            return
        # create_button_template関数を使用してボタンテンプレートを生成
        message_template = create_button_template(keywords_list)

        # ボタンテンプレートをLINEに送信
        line_bot_api.reply_message(
            event.reply_token,
            message_template
        )

    except Exception as e:
        print(f"Error handling message: {e}")
        traceback.print_exc()

@handler.add(PostbackEvent)
def on_postback(event):
    try:
        # Postbackで受け取ったデータ（キーワード）を確認
        selected_keyword = event.postback.data
        print(f"ユーザーが選択したキーワード: {selected_keyword}")  # デバッグ用に出力
        
        # 選択されたキーワードからカテゴリを取得
        df_keyword = fetch_recipe_categories(selected_keyword)
        if df_keyword.empty:
            raise NoRecipeFoundError("該当するレシピが見つかりませんでした。別のキーワードで再検索してください。")
        
        df_recipe = fetch_recipe_category_ranking(df_keyword)
        if df_recipe.empty:
            raise NoRecipeFoundError("該当するレシピが見つかりませんでした。別のキーワードで再検索してください。")
        
        # カルーセルテンプレートの作成
        carousel_template = create_carousel_template(df_recipe)

        # カルーセルテンプレートをLINEに送信
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="トップ4のレシピ",
                template=carousel_template
            )
        ) 
    except NoRecipeFoundError as e:
        # 該当するレシピが見つからなかった場合のエラーメッセージ
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{e.message}")
        )
    except Exception as e:
        # 予期しないエラーの処理
        print(f"Error handling postback: {e}")
        traceback.print_exc()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="エラーが発生しました。もう一度お試しください。")
        )   


# # お気に入り登録ボタンを押したとき
# @handler.add(PostbackEvent)
# def on_postback(event):
#   # レシピタイトル、レシピURL、画像URLを取得
#   data = event.postback.data
#   recipe_title, recipe_url, food_image_url = data.split("|")

#   # ユーザID
#   user_id = event.source.user_id

#   # あけぴさん、DBに保存する処理をここに書く

#   # DBに登録後、メッセージをLINEに表示する
#   line_bot_api.reply_message(
#     event.reply_token,
#     TextSendMessage(text=f'「{recipe_title}」をお気に入り登録しました！')
#   )

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)