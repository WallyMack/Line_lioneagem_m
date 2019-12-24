#app.py
import os
import psycopg2 as pg
import pandas as pd
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('3AlYHVFd4qJMZPPqkGJR3XtBQEJlsvpMTbJJthYmCTZtE2Qn9jL1zm0pP436TIOgMs7RpmXPM9UM1SML94pvsuxd6cimxyqWvGSUWcN/JlCtkj4YAQCQOGSjJOe9WVaOuCtrWsNX3nlZLwj6Ds9jQgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d012d795164d814bc796f34d91aa5562')



@app.route("/")
def hell():
    return "Hello World!"

@app.route("/test")
def hello():
    return "Hello World!"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        if str.lower(event.message.text) == 'boss':
            conn = pg.connect(host = '34.80.112.249',database = 'Line',user = 'postgres', password = '1qaz@WSX', port = 5432)
            cur = conn.cursor()
            sql_select = """
            select king_name, '地圖('||region ||')' as region ,to_char(kill_date, 'HH24:MI:SS') from lioneagem_m where kill_date is not null order by kill_date
            """
            sql_null = """
            select king_name, '地圖('||region ||')' as region ,'' from lioneagem_m where kill_date is null
            """
            cur.execute(sql_select)
            result = cur.fetchall()
            cur.execute(sql_null)
            result1 = cur.fetchall()
            df_result = pd.DataFrame(result)
            df_result1 = pd.DataFrame(result1)
            list_ = [df_result.to_string(index=False ,header = False, justify = 'left'),'\n','==============','\n', df_result1.to_string(index=False,header = False, justify = 'left')]
            return_value = ''.join(list_)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=return_value))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run('0.0.0.0', port=os.environ['PORT'])