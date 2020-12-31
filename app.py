# coding: utf-8
from flask import Flask, request, abort, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
import uuid
import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    FollowEvent,
    UnfollowEvent,
    MessageEvent,
    TextMessage,
    TextSendMessage,
    StickerSendMessage,
    FlexSendMessage,
)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__, static_folder='static')
CORS(app)

# Liff ID
REGIST_LIFF_ID = os.environ.get("REGIST_LIFF_ID")
FEEDBACK_LIFF_ID = os.environ.get("FEEDBACK_LIFF_ID")

# LINE BOTの設定
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')
CHANNEL_ID = os.environ.get('LIFF_CHANNEL_ID')
RICH_MENU_ID = os.environ.get('RICH_MENU_ID')
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route('/regist')
def regist():
    return render_template('regist.html', registLiffId=REGIST_LIFF_ID)


@app.route('/feedback')
def feedback():
    return render_template('feedback.html', feedbackLiffId=FEEDBACK_LIFF_ID)


@app.route('/submit', methods=['POST'])
def submit():
    body = request.get_json()
    app.logger.info('Request body: ' + json.dumps(body))
    # get user data
    data = {
        'id_token': body['token'],
        'client_id': CHANNEL_ID
    }
    verifyed_data = requests.post(
        'https://api.line.me/oauth2/v2.1/verify', data=data).json()
    # リッチメニューを設定
    user_id = verifyed_data['sub']
    line_bot_api.link_rich_menu_to_user(user_id, RICH_MENU_ID)

    response = {
        "message": "OK!",
        "status": 200
    }
    return jsonify(response)


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # Connect Check
    data = json.loads(body)
    if not data["events"]:
        return "OK"

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(FollowEvent)
def handle_follow(event):
    message = "{}{}".format(
        '8.comへようこそ！はじめに以下から8.comのユーザー登録をしましょう',
        '\n※このアカウントは空想上のプロトタイプなので、実際の挙動とは異なります')
    regist_button = {
        "type": "flex",
        "altText": "会員登録のお願い",
        "contents": {
            "type": "bubble",
            "direction": "ltr",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "こちらから会員登録お願いします",
                        "align": "center",
                        "contents": []
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "会員登録",
                            "uri": "https://liff.line.me/1655537406-dWMvnRDm"
                        },
                        "style": "primary"
                    }
                ]
            }
        }
    }
    button_object = FlexSendMessage.new_from_json_dict(regist_button)
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=message),
            button_object,
            StickerSendMessage(
                package_id=11537,
                sticker_id=52002739
            )
        ]
    )


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    line_bot_api.unlink_rich_menu_from_user(event.source.user_id)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == 'フィードバック':
        form_button = {
            "type": "flex",
            "altText": "フィードバックのご案内",
            "contents": {
                "type": "bubble",
                "direction": "ltr",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "今回のお料理の評価をお願いします",
                            "align": "center",
                            "contents": []
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "フィードバックを書く",
                                "uri": "https://liff.line.me/1655537406-ed0l8oJx"
                            },
                            "style": "primary"
                        }
                    ]
                }
            }
        }
        button_object = FlexSendMessage.new_from_json_dict(form_button)
        line_bot_api.reply_message(event.reply_token, button_object)
    elif event.message.text == 'チケット':
        ticket_obj = {
            "type": "flex",
            "altText": "チケット",
            "contents": {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_2_restaurant.png",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "Eight burger",
                            "weight": "bold",
                            "size": "xl",
                            "gravity": "center",
                            "wrap": True,
                            "contents": []
                        },
                        {
                            "type": "text",
                            "text": "こちらのチケットをお持ちいただき、店舗へお越しください。",
                            "wrap": True,
                            "contents": []
                        },
                        {
                            "type": "text",
                            "text": "有効期限：2021年5月5日",
                            "size": "xs",
                            "color": "#AAAAAA",
                            "margin": "xxl",
                            "wrap": True,
                            "contents": []
                        }
                    ]
                }
            }
        }
        ticket_message = FlexSendMessage.new_from_json_dict(ticket_obj)
        line_bot_api.reply_message(event.reply_token, ticket_message)
    else:
        message_obj = TextSendMessage(text=event.message.text)
        line_bot_api.reply_message(event.reply_token, message_obj)


if __name__ == "__main__":
    app.debug = True
    app.run()
