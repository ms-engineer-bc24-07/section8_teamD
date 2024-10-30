import requests
import os
import json

# 楽天APIからカテゴリ一覧を取得してキャッシュに保存する
def fetch_and_cache_categories():
    url = "https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426"
    params = {
        "format": "json",
        "applicationId": os.getenv("RAKUTEN_APPLICATION_ID")
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        json_data = response.json()
        categories = []

        # 大カテゴリ
        for category in json_data['result']['large']:
            categories.append(category['categoryName'])

        # 中カテゴリ
        for category in json_data['result']['medium']:
            categories.append(category['categoryName'])

        # 小カテゴリ
        for category in json_data['result']['small']:
            categories.append(category['categoryName'])

        # キャッシュに保存
        with open("categories_cache.json", "w", encoding="utf-8") as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)
        return categories
    else:
        raise Exception("Failed to fetch data from Rakuten API")

# キャッシュからカテゴリ一覧を読み込む
def load_categories_from_cache():
    if os.path.exists("categories_cache.json"):
        with open("categories_cache.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return fetch_and_cache_categories()
