#app.py
import os
import psycopg2 as pg
import pandas as pd
import time
from datetime import datetime, timedelta
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



def connector_db():
    conn = pg.connect(host='34.80.112.249', database='Line', user='postgres', password='1qaz@WSX', port=5432)
    cur = conn.cursor()
    sql_select = """
    select king_name,'地圖('||region ||')' as region,kill_date,Rebirth_time
    from lioneagem_m where kill_date is not null
    order by kill_date
            """
    sql_null = """
    select king_name, '地圖('||region ||')' as region ,'' 
    from lioneagem_m where kill_date is null
    """
    cur.execute(sql_select)
    result = cur.fetchall()
    cur.execute(sql_null)
    result1 = cur.fetchall()
    df_result1 = pd.DataFrame(result1)
    check_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    run_time = datetime.strptime(check_time, '%Y-%m-%d %H:%M:%S')
    total_list = []
    for i in result:
        data = list(i)
        if run_time - data[2] >= timedelta(hours=0):
            while run_time - data[2] >= timedelta(hours=0):
                data[2] = data[2] + timedelta(hours=i[-1])
            data[3] = data[2]
            print('* ' + str(data[2]))
            data[2] = '* ' + str(data[2].strftime("%H:%M:%S"))
            
        else:
            data[3] = data[2]
            data[2] = data[2].strftime("%H:%M:%S")

        total_list.append(tuple(data))

    value = pd.DataFrame(total_list).sort_values(3)
    value.pop(3)
    list_ = [value.to_string(index=False, header=False), '\n', '==============', '\n',
    df_result1.to_string(index=False, header=False)]
    response_message = ''.join(list_)
    print(response_message)
    return response_message

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
            conn = pg.connect(host='34.80.112.249', database='Line', user='postgres', password='1qaz@WSX', port=5432)
            cur = conn.cursor()
            sql_select = """
    select king_name,'地圖('||region ||')' as region,kill_date,Rebirth_time
    from lioneagem_m where kill_date is not null
    order by kill_date
            """
            sql_null = """
    select king_name, '地圖('||region ||')' as region ,'' 
    from lioneagem_m where kill_date is null
    """
            cur.execute(sql_select)
            result = cur.fetchall()
            cur.execute(sql_null)
            result1 = cur.fetchall()
            df_result1 = pd.DataFrame(result1)
            check_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            run_time = datetime.strptime(check_time, '%Y-%m-%d %H:%M:%S')
            total_list = []
            for i in result:
                data = list(i)
                if run_time - data[2] >= timedelta(hours=0):
                    while run_time - data[2] >= timedelta(hours=0):
                        data[2] = data[2] + timedelta(hours=i[-1])

                    data[3] = data[2]
                    print('* ' + str(data[2]))
                    data[2] = '* ' + str(data[2].strftime("%H:%M:%S"))
            
                else:
                    data[3] = data[2]
                    data[2] = data[2].strftime("%H:%M:%S")

                total_list.append(tuple(data))

            value = pd.DataFrame(total_list).sort_values(3)
            value.pop(3)
            list_ = [value.to_string(index=False, header=False), '\n', '==============', '\n',
            df_result1.to_string(index=False, header=False)]
            response_message = ''.join(list_)
            print(response_message)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response_message))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run('0.0.0.0', port=os.environ['PORT'])