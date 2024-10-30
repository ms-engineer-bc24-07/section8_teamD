from linebot.models import TextSendMessage

# お気に入りの登録機能
def add_to_favorites(user_id, recipe_title, recipe_url, food_image_url):
    # DB保存ロジック
    pass

# お気に入りのリストを取得して表示
def get_favorites(user_id):
    # DBからお気に入りリストを取得するロジック
    favorites = []  # 例: [{'title': 'レシピ名1', 'url': 'レシピURL1'}, ...]
    if not favorites:
        return TextSendMessage(text="お気に入りが登録されていません。")
    else:
        messages = [TextSendMessage(text=f"{fav['title']}: {fav['url']}") for fav in favorites]
        return messages
