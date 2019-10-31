import paho.mqtt.client as mqtt
import json
from wakeonlan import send_magic_packet
import requests
import time
import os
import settings.py

# beebotteのデータ
TOKEN = settings.TOKEN
HOSTNAME = settings.HOSTNAME
PORT = settings.PORT
ADDRESS = settings.ADDRESS
CACERT = settings.CACERT

# WOLホストPCのデータ
MACADDR = settings.MACADDR
IPADDR = settings.IPADDR

# slack webhock APIのURL
url = settings.SLACKURL

# wol用のメッセージ
BOOTUP_WORD = settings.BOOTUP_WORD

# json形式で送るデータ
item_data = {
    'channel': '#wol',
    'text': 'これはwol_kai.pyからの投稿です'
}

def on_connect(client, userdata, flags, respons_code):
    #時刻の取得
    time_str = time.strftime("%Y/%m/%d %H:%M", time.strptime(time.ctime()))
    #slackへの投稿
    item_data['text'] = '接続に成功しました\n' + time_str
    r_post = requests.post(url, json=item_data)
    #結果の表示
    print("slack response:")
    print(r_post.status_code)
    print(r_post.text)
    print("beebotte result:")
    print('status {0}'.format(respons_code))
    client.subscribe(ADDRESS)

def on_message(client, userdata, msg):
    print("beebotte result:")
    print(msg.topic + " " + str(msg.payload))
    message = json.loads(msg.payload.decode("utf-8"))["data"]
    print("data: " + message)
    if message == BOOTUP_WORD:
        #WOL用のマジックパケットを送信
        send_magic_packet(MACADDR)
        #時刻の取得
        time_str = time.strftime("%Y/%m/%d %H:%M", time.strptime(time.ctime()))
        #slackへの投稿
        item_data['text'] = 'WOLを実行しました\n' + time_str
        r_post = requests.post(url, json=item_data)
        #結果の表示
        print("slack response:")
        print(r_post.status_code)
        print(r_post.text)
        print("result:")
        print("WOL EXECUTED")
    elif message == "PING":
        #時刻の取得
        time_str = time.strftime("%Y/%m/%d %H:%M", time.strptime(time.ctime()))
        #slackへの投稿
        item_data['text'] = 'pingを受け取りました\n' + time_str
        r_post = requests.post(url, json=item_data)
        #結果の表示
        print("slack response:")
        print(r_post.status_code)
        print(r_post.text)
        print("result:")
        print("PING EXECUTED")
    else:
        #時刻の取得
        time_str = time.strftime("%Y/%m/%d %H:%M", time.strptime(time.ctime()))
        #slackへの投稿
        item_data['text'] = 'メッセージが違います\n' + time_str
        r_post = requests.post(url, json=item_data)
        #結果の表示
        print("slack response:")
        print(r_post.status_code)
        print(r_post.text)
        print("result:")
        print("WOL NOT EXECUTED")


client = mqtt.Client()
client.username_pw_set("token:%s"%TOKEN)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(os.path.join(os.path.dirname(__file__), CACERT))
client.connect(HOSTNAME, port=PORT, keepalive=60)
client.loop_forever()
