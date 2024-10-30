import traceback
from flask import Flask, request, abort
from firebase.main import upload_to_firestore
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

import firebase_admin
from firebase_admin import credentials

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
        # Postbackで受け取ったデータを確認
        postback_data = event.postback.data
        print(f"ユーザーが選択したデータ: {postback_data}", flush=True)  # デバッグ用に出力

        # 3択のキーワード選択処理 (データが "select:" で始まる場合)
        if postback_data.startswith("select:"):
            selected_keyword = postback_data.split("select:")[1]
            print(f"選択されたキーワード: {selected_keyword}", flush=True)
            df_keyword = fetch_recipe_categories(selected_keyword)

            if df_keyword.empty:
                raise NoRecipeFoundError("該当するレシピが見つかりませんでした。別のキーワードで再検索してください。")

            # レシピの取得
            df_recipe = fetch_recipe_category_ranking(df_keyword)
            if df_recipe.empty:
                raise NoRecipeFoundError("該当するレシピが見つかりませんでした。別のキーワードで再検索してください。")

            # カルーセルテンプレートの作成
            carousel_template = create_carousel_template(df_recipe)
            line_bot_api.reply_message(
                event.reply_token,
                [TextSendMessage(text=f"{selected_keyword}"),
                TemplateSendMessage(
                    alt_text="トップ4のレシピ",
                    template=carousel_template
                )]
            )

        # お気に入り追加処理 (データが "favorite:" で始まる場合)
        elif postback_data.startswith("favorite:"):
            # レシピ情報（タイトル、レシピURL，画像URL）を取得
            recipe_infos = postback_data.replace("favorite:", "")
            recipe_info = recipe_infos.split("|")
            recipe_id, recipe_title, recipe_url, food_image_url = recipe_info

            # ユーザーIDを取得
            user_id = event.source.user_id

            # DBに保存する処理をここに記述（例: save_to_favorites(user_id, recipe_id, recipe_title, recipe_url, food_image_url)）
            upload_to_firestore(user_id, recipe_id, recipe_title, recipe_url, food_image_url)

            # お気に入り登録完了のメッセージをLINEに送信
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f'「{recipe_title}」をお気に入りに追加しました！')
            )

    except NoRecipeFoundError as e:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{e.message}")
        )
    except Exception as e:
        print(f"Error handling postback: {e}")
        traceback.print_exc()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="エラーが発生しました。もう一度お試しください。")
        )

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)

  default_app = firebase_admin.initialize_app()