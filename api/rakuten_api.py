import os
import time
import requests
import pandas as pd

def fetch_recipe_categories(recipe_keyword):
  print(recipe_keyword, flush=True)

  # 楽天レシピのカテゴリー覧を取得
  url = "https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426"
  params = {
    "format": "json",
    "applicationId": os.getenv("RAKUTEN_APPLICATION_ID")
  }
  response = requests.get(url, params=params)
  
  if response.status_code == 200:
    json_data = response.json()

    # mediumカテゴリの親カテゴリのデータフレーム
    parent_dict = {}

    # 全カテゴリの、categoryNameとcategoryId（Rakuten Category Ranking APIの入力パラメーター用）をセットするデータフレーム
    df = pd.DataFrame(columns=['categoryId','categoryName'])  # categoryNameあとで消してもいいかも

    # 大カテゴリ
    for category in json_data['result']['large']:
      df2 = pd.DataFrame(
        [[ category['categoryId'], category['categoryName'] ]],
        columns=['categoryId', 'categoryName']
      )
      df = pd.concat([df, df2], ignore_index=True)

    # 中カテゴリ
    for category in json_data['result']['medium']:
      df2 = pd.DataFrame(
        [[
          str(category['parentCategoryId']) + "-" + str(category['categoryId']),
          category['categoryName']
        ]],
        columns=['categoryId', 'categoryName']
      )
      df = pd.concat([df, df2], ignore_index=True)
      parent_dict[str(category['categoryId'])] = category['parentCategoryId']

    # 小カテゴリ
    for category in json_data['result']['small']:
      df2 = pd.DataFrame(
        [[
          parent_dict[category['parentCategoryId']] + "-" + str(category['parentCategoryId'])+ "-" + str(category['categoryId']),
          category['categoryName']
        ]],
        columns=['categoryId', 'categoryName']
      )
      df = pd.concat([df, df2], ignore_index=True)

    # print(df, flush=True)

    # キーワードを含むカテゴリを抽出
    df_keyword = df.query('categoryName.str.contains(@recipe_keyword)', engine='python')
    # print(df_keyword, flush=True)
    # print(df_keyword["categoryId"], flush=True)

    # categories = df_keyword["categoryId"]
    # combined_string = categories.str.cat(sep=", ")

    return df_keyword
  else:
    raise Exception("Failed to fetch data from Rakuten API")


def fetch_recipe_category_ranking(df):
  df_recipe = pd.DataFrame(
    columns = [
      'recipeId',
      'recipeTitle',
      'foodImageUrl',
      'recipeMaterial',
      'recipeCost',
      'recipeIndication',
      'categoryId',
      'categoryName'
    ]
  )

  for _, row in df.iterrows():
    time.sleep(1) 
    url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
    params = {
      "applicationId": os.getenv("RAKUTEN_APPLICATION_ID"),
      "categoryId": row['categoryId']
    }
    response = requests.get(url, params=params)
    print("--------", flush=True)
    print(response.json(), flush=True)
