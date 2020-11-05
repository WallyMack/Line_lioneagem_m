import os
import psycopg2 as pg
import pandas as pd
import time
import re
import requests
from datetime import datetime, timedelta

def update_boss(query):
    try:
        conn = pg.connect(host='127.0.0.1', database='line', user='postgres', password='1qaz@WSX', port=5432)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        conn.close()
        return '更新成功'
    except Exception as e:
        print(e, flush=True)
        conn.rollback()
        conn.close()
        return '更新失敗'


def lineNotifyMessage(token, msg):
    headers = {
          "Authorization": "Bearer " + token, 
          "Content-Type" : "application/x-www-form-urlencoded"
    }
	
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code
	

if __name__ == "__main__":
    try:
        print('check boss time ready push message', flush=True)
        conn = pg.connect(host='127.0.0.1', database='line', user='postgres', password='1qaz@WSX', port=5432)
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
        now_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        now_time = datetime.strptime(now_timestamp, '%Y-%m-%d %H:%M:%S')
        boss_list = []
        for i in result:
            value = (i[2] - now_time)
            clear_time = (now_time - i[2])
            if value.seconds < 600 and value.days == 0:
                value = i[2] - now_time
                value = re.sub(r'\..*','',str(value))
                hours = value.split(':')[1]
                mins = value.split(':')[2]
                boss_list.append(tuple([i[0],i[1],hours,mins]))
            elif clear_time.days == 1:
                Sql_update = """
update lioneagem_m set kill_date = null where region = {}
        """
                return_status = update_boss(sql_update.format(i[1]))
                print('boss time over one day clear: ',i[1])
                
        message_box = []
        for i in boss_list:
            message_box.append('【提醒】{} 地圖的 {} 將在 {}分鐘 {}秒後重生\n'.format(i[1], i[0], i[2], i[3]))
        if message_box:
            print(now_time, message_box, flush=True)
            token = 'sEBvtvnNwAtdLxYcVtHyrp643e2hI25I2KIbWaW9gq7'
            lineNotifyMessage(token, message_box)
            # line_bot_api.push_message("C40c1a34472356970900a8a99dd4d8531", TextSendMessage(text='{}'.format(''.join(message_box))))
    except Exception as e:
        print('check boss time error: ', e, flush=True)
        conn.rollback()
        conn.close()
