import os
import time
import requests
import pandas as pd

# 独自例外クラスの定義
class NoRecipeFoundError(Exception):
  def __init__(self, message="該当するレシピが見つかりませんでした。別のキーワードで再検索してください。"):
    self.message = message
    super().__init__(self.message)

# 楽天レシピカテゴリ一覧API から、全カテゴリのカテゴリIDとカテゴリ名を取得する
def fetch_recipe_categories(recipe_keyword):
  print(f"OpenAI APIから渡されたキーワード: {recipe_keyword}", flush=True)

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

    columns=['categoryId','categoryName']

    # 全カテゴリの、categoryNameとcategoryId（楽天レシピカテゴリ別ランキングAPIの入力パラメーター用）をセットするデータフレーム
    df = pd.DataFrame(columns=columns)  # categoryNameあとで消してもいいかも？

    # 大カテゴリ
    for category in json_data['result']['large']:
      df2 = pd.DataFrame(
        [[ category['categoryId'], category['categoryName'] ]],
        columns=columns
      )
      df = pd.concat([df, df2], ignore_index=True)

    # 中カテゴリ
    for category in json_data['result']['medium']:
      df2 = pd.DataFrame(
        [[
          str(category['parentCategoryId']) + "-" + str(category['categoryId']),
          category['categoryName']
        ]],
        columns=columns
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
        columns=columns
      )
      df = pd.concat([df, df2], ignore_index=True)

    # キーワードを含むカテゴリを抽出
    df_keyword = df.query('categoryName.str.contains(@recipe_keyword)', engine='python')

    # 抽出結果が0件のとき
    if df_keyword.empty:
      raise NoRecipeFoundError()
    # 抽出結果が2件以上で、同じ分類のとき
    elif len(df_keyword) >= 2 and (str(df_keyword.iloc[0]['categoryId']) in str(df_keyword.iloc[1]['categoryId'])):
        df_keyword = df_keyword.drop(index=df_keyword.index[0]).reset_index(drop=True)
    # カテゴリが複数あるとき
    else:
      print("*******該当するカテゴリが複数存在します。*******", flush=True)
    return df_keyword
  else:
    raise Exception("Failed to fetch data from Rakuten API")

# 楽天レシピカテゴリ別ランキングAPI から、カテゴリ内のレシピのトップ4を取得する
def fetch_recipe_category_ranking(df):
  columns = [
    'recipeId',           # レシピID
    'recipeTitle',        # レシピタイトル
    'recipeUrl',          # レシピURL（httpsではじまるレシピURL）
    'foodImageUrl',       # 画像のURL(サイズ:小　httpsではじまる商品画像(70x70ピクセル)のURL）
    # 'recipeMaterial',   # 材料名の一覧
    'recipeIndication',   # 調理時間目安
    'recipeCost',         # 費用の目安
    'rank'                # ランキング順位
  ]

  # カテゴリのトップ4レシピのデータフレーム
  df_recipe = pd.DataFrame(
    columns=columns
  )

  for _, row in df.iterrows():
    # 先方のサーバに負荷がかからないように少し待つ
    time.sleep(1)

    # 楽天レシピのカテゴリー覧を取得
    url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
    params = {
      "applicationId": os.getenv("RAKUTEN_APPLICATION_ID"),
      "categoryId": row['categoryId']
    }
    response = requests.get(url, params=params)
    json_data = response.json()
    recipes = json_data['result']

    for recipe in recipes:
      df2 = pd.DataFrame(
        [[
          recipe['recipeId'],
          recipe['recipeTitle'],
          recipe['recipeUrl'],
          recipe['foodImageUrl'],
          # recipe['recipeMaterial'],
          recipe['recipeIndication'],
          recipe['recipeCost'],
          recipe['rank'],
        ]],
        columns=columns
      )
      df_recipe = pd.concat([df_recipe, df2], ignore_index=True)

  return df_recipe
