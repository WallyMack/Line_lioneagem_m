# app.py
import os
import psycopg2 as pg
import pandas as pd
import time
import re
from datetime import datetime, timedelta
from flask import Flask, request, abort
from apscheduler.schedulers.blocking import BlockingScheduler

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
turn_on = False
sched = BlockingScheduler()
line_bot_api = LineBotApi(
    '3AlYHVFd4qJMZPPqkGJR3XtBQEJlsvpMTbJJthYmCTZtE2Qn9jL1zm0pP436TIOgMs7RpmXPM9UM1SML94pvsuxd6cimxyqWvGSUWcN/JlCtkj4YAQCQOGSjJOe9WVaOuCtrWsNX3nlZLwj6Ds9jQgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d012d795164d814bc796f34d91aa5562')

def query_boss(query):
    try:
        conn = pg.connect(host='34.80.112.249', database='Line', user='postgres', password='1qaz@WSX', port=5432)
        cur = conn.cursor()
        if str.isdigit(query):
            sql = """
    select region
    from lioneagem_m where region in ({})
            """.format(query)
        elif str.isalnum(query):
            sql = """
            select king_name
            from lioneagem_m where king_name in ('{}')
                    """.format(query)
        cur.execute(sql)
        result = cur.fetchall()
        conn.close()
        return result

    except Exception as e:
        print(e)
        conn.rollback()
        conn.close()
        return '查詢失敗'



def update_boss(query):
    try:
        conn = pg.connect(host='34.80.112.249', database='Line', user='postgres', password='1qaz@WSX', port=5432)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        conn.close()
        return '更新成功'
    except Exception as e:
        print(e)
        conn.rollback()
        conn.close()
        return '更新失敗'


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
    print(df_result1)
    if result:
        check_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 28800))
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
        conn.close()
        return response_message
    else:
        list_ = ['==============', '\n', df_result1.to_string(index=False, header=False)]
        response_message = ''.join(list_)
        print(response_message)
        conn.close()
        return response_message


@app.route("/")
def switch():
    global turn_on
    status = not turn_on
    if not status:
        turn_on = False
        sched.shutdown()
        yield '自動提醒關閉'
    else:
        turn_on = True
        yield '自動提醒開啟'
        sched.start()


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
            response_message = connector_db()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response_message))

        elif str.lower(event.message.text) == 'help':
            help_box = """
使用方式：
1. 輸入『boss』查看王的重生時間
2. 輸入『王 死亡時間』可更新重生時間(例如『奇岩 21:00:00』/ 『15 21:00:00』) ，系統會推算下一隻為22:00:00
3. 輸入『clean』就可清除所有王時間
4. Boss時間如果沒有更新，系統會自動幫你推算下一隻，並在時間前面加上＊號，如『奇岩(地圖18) - ＊ 01:14:05』
5. 輸入『help』可查看使用方式

            """
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=help_box))

        elif len(str.lower(event.message.text).split(' ')) == 2:
            update_message = event.message.text.split(' ')
            if str.isdigit(update_message[0]):
                boss = query_boss(update_message[0])
                if not boss:
                    return_status = '{} : 這打王區域不存在'.format(update_message[0])
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=return_status))
                SQL = tuple(update_message)
                yyyymmdd = [time.strftime("%Y-%m-%d", time.localtime(time.time() + 28800))]
                yyyymmdd.append(SQL[1])
                update_time = ' '.join(yyyymmdd)
                sql_update = """
    update lioneagem_m set kill_date = timestamp '{}' + interval '1 hour' * Rebirth_time where region = {}
            """
                sql_systanx = sql_update.format(update_time, SQL[0])
                return_status = update_boss(sql_systanx)

                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=return_status))

            elif str.isalnum(update_message[0]):
                boss = query_boss(update_message[0])
                if not boss:
                    return_status = '{} : 這隻王不存在'.format(update_message[0])
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=return_status))
                SQL = tuple(update_message)
                yyyymmdd = [time.strftime("%Y-%m-%d", time.localtime(time.time() + 28800))]
                yyyymmdd.append(SQL[1])
                update_time = ' '.join(yyyymmdd)
                sql_update = """
    update lioneagem_m set kill_date = timestamp '{}' + interval '1 hour' * Rebirth_time where king_name = '{}'
            """
                sql_systanx = sql_update.format(update_time, SQL[0])
                return_status = update_boss(sql_systanx)

                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=return_status))

        elif str.lower(event.message.text) == 'clean':

            sql_update = """
    update lioneagem_m set kill_date = null where clean = 0
            """
            return_status = update_boss(sql_update)
            if return_status == '更新成功':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='王時間全部清除完成'))

        elif str.lower(event.message.text) == '!alert':
            value = switch()
            ans = list(value)
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='{}'.format(ans[0])))

@sched.scheduled_job('interval', minutes=2)
def push_boss_time():
    try:
        conn = pg.connect(host='34.80.112.249', database='Line', user='postgres', password='1qaz@WSX', port=5432)
        cur = conn.cursor()
        Sql = """
select king_name, region, kill_date
from lioneagem_m 
where kill_date is not null
order by kill_date
        """
        cur.execute(Sql)
        result = cur.fetchall()
        conn.close()
        now_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 28800))
        now_time = datetime.strptime(now_timestamp, '%Y-%m-%d %H:%M:%S')
        boss_list = []
        for i in result:
            value = (i[2] - now_time)
            if value.seconds < 600:
                value = i[2] - now_time
                value = re.sub(r'\..*','',str(value))
                hours = value.split(':')[1]
                mins = value.split(':')[2]
                boss_list.append(tuple([i[0],i[1],hours,mins]))

        message_box = []
        for i in boss_list:
            message_box.append('【提醒】{} 地圖的 {} 將在 {}分鐘 {}秒後重生\n'.format(i[1], i[0], i[2], i[3]))
        if message_box:
            line_bot_api.push_message("C40c1a34472356970900a8a99dd4d8531", TextSendMessage(text='{}'.format(''.join(message_box))))
    except Exception as e:
        print('check boss time error: ', e)
        conn.rollback()
        conn.close()

if __name__ == "__main__":
    app.run('0.0.0.0', port=os.environ['PORT'])
