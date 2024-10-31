import openai
import os
from api.rakuten_category_cache import load_categories_from_cache

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_keywords(user_message):
        # キャッシュからカテゴリ一覧を読み込む
    category_list = load_categories_from_cache()
    prompt = (
        f"以下は楽天の料理カテゴリ一覧です:\n{', '.join(category_list)}\n"
        f"次の材料組み合わせてできる料理や料理時間にあったカテゴリを楽天の料理カテゴリから３つ提案してください。"
        f"カテゴリの単語のみを返してください。-や数字や余分な説明は入れないでください。:\n\n{user_message}"
    )
    response = openai.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
    keywords_text = response.choices[0].message.content.strip()
    keywords_list = [keyword.strip() for keyword in keywords_text.splitlines() if keyword]  # 3つのキーワードをリスト形式で取得
    return keywords_list[:3]  