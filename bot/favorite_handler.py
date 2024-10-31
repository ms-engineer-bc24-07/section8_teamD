from google.cloud import firestore
from linebot.models import TextSendMessage

def initialize_firestore():
    try:
        key_gcf = './serviceAccountKey.json' 
        return firestore.Client.from_service_account_json(key_gcf)
    except Exception as e:
        print("Firestore connection error:", e)


db = initialize_firestore()

# お気に入りのリストを表示
def get_favorites(user_id):
    favorites_ref = db.collection("recipes").where("userID", "==", user_id)
    docs = favorites_ref.stream()
    favorites = [{"title": doc.to_dict().get("recipeTitle"), "url": doc.to_dict().get("recipeURL")} for doc in docs]  # 例: [{'title': 'レシピ名1', 'url': 'レシピURL1'}, ...]
    if not favorites:
        return TextSendMessage(text="お気に入りが登録されていません。")
    else:
        messages = [TextSendMessage(text=f"{fav['title']}: {fav['url']}") for fav in favorites]
        return messages
