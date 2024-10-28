import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_keywords(user_message):
    prompt = f"次の材料や料理時間、気分に最も適した料理レシピのキーワードを一つだけ教えてください: {user_message}"
    response = openai.chat.completions.create(
            model="gpt-4o",  # 必要に応じてモデルを変更
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
    keywords = response.choices[0].message.content.strip()
    return keywords