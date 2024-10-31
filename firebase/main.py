from datetime import datetime
from google.cloud import firestore

def upload_to_firestore(user_id, recipe_id, recipe_title, recipe_url, food_image_url):
    # JSONファイルのパス
    key_gcf = 'serviceAccountKey.json'
    # JSONファイルを用いて Firestore に接続
    db = firestore.Client.from_service_account_json(key_gcf)
    # 保存したいデータを辞書型で用意
    data = {
        "userID":user_id,
        "recipeId": recipe_id,
        "recipeTitle": recipe_title,
        "recipeURL":recipe_url,
        "foodImageURL":food_image_url,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    # データを保存
    db.collection("recipes").add(data)