# button_template.py

from linebot.models import TemplateSendMessage, ButtonsTemplate, PostbackAction

def create_button_template(keywords_list):
    """
    カテゴリ候補のリストからボタンテンプレートメッセージを作成する関数
    """
    # ボタンテンプレートメッセージを作成
    message_template = TemplateSendMessage(
        alt_text="キーワード候補",
        template=ButtonsTemplate(
            title="どの料理を作りたいですか？",
            text="次の中から選んでください:",
            actions=[
                PostbackAction(label=keyword[:20], data=keyword) for keyword in keywords_list
            ]
        )
    )
    return message_template
