import os
import openai
from linebot.models import TextSendMessage

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ingredient_substitute(ingredient):
    #代替材料を提案
    prompt = f"「{ingredient}」の代わりに使える材料を教えてください。"
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
    
        substitute_info = response.choices[0].message.content.strip()
        # メッセージ整形
        formatted_message = substitute_info.replace("**", "").replace("。 ", "。\n")
    
        return TextSendMessage(text=formatted_message)

    except Exception as e:
        print(f"Error fetching substitute: {e}")
        return TextSendMessage(text="代替材料の提案ができませんでした。もう一度お試しください。")
