import paho.mqtt.client as mqtt
import json
from wakeonlan import send_magic_packet
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

# wol用のメッセージ
BOOTUP_WORD = settings.BOOTUP_WORD

def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    client.subscribe(ADDRESS)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    message = json.loads(msg.payload.decode("utf-8"))["data"]
    print("data: " + message)
    if message == BOOTUP_WORD:
        print("WOL EXECUTE")
        send_magic_packet(MACADDR)

client = mqtt.Client()
client.username_pw_set("token:%s"%TOKEN)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(os.path.join(os.path.dirname(__file__), CACERT))
client.connect(HOSTNAME, port=PORT, keepalive=60)
client.loop_forever()
