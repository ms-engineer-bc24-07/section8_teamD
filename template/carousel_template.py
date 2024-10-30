from linebot.models import CarouselTemplate, CarouselColumn, URIAction, PostbackTemplateAction

# カルーセルテンプレートを作成する
def create_carousel_template(df_recipe):
  columns = [
    CarouselColumn(
      thumbnail_image_url = f"{df_recipe.iloc[i]['foodImageUrl']}",
      title = f"{df_recipe.iloc[i]['recipeTitle']}",
      text = f"{df_recipe.iloc[i]['rank']}位　調理時間目安：{df_recipe.iloc[i]['recipeIndication']}",
      actions = [
        PostbackTemplateAction(
          label = 'お気に入り登録',
          data=f"{df_recipe.iloc[i]['recipeTitle']}|{df_recipe.iloc[i]['recipeUrl']}|{df_recipe.iloc[i]['foodImageUrl']}"
        ),
        URIAction(
          type="uri",
          label="レシピを見る",
          uri=f"{df_recipe.iloc[i]['recipeUrl']}"
        )
      ]
    ) for i in range(len(df_recipe))
  ]
  
  return CarouselTemplate(columns=columns)
