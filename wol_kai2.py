import paho.mqtt.client as mqtt
import json
from wakeonlan import send_magic_packet
import requests
import time
import os
import paramiko
import socket
import settings

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
URL = settings.SLACKURL

# SSH用のデータ
PORT_SSH = settings.PORT_SSH
HOST_USER = settings.HOST_USER
KEY_FILE = settings.KEY_FILE
PASSPHRASE = settings.PASSPHRASE

# ホストPCのpsshutdown.exeのPATH
PSSD_PATH = settings.PSSD_PATH

# wol用のメッセージ
BOOTUP_WORD = settings.BOOTUP_WORD
SLEEP_WORD = settings.SLEEP_WORD
SLEEP_LATER_WORD = settings.SLEEP_LATER_WORD
SHUTDOWN_WORD = settings.SHUTDOWN_WORD
SHUTDOWN_LATER_WORD = settings.SHUTDOWN_LATER_WORD


def slack_post(text):
    item_data = {
        'channel': '#wol',
        'text': text + '\n' + time.strftime("%Y/%m/%d %H:%M", time.strptime(time.ctime()))
    }
    r_post = requests.post(URL, json=item_data)

def ssh_exec(command):
    try:
        SSH.connect(IPADDR, PORT_SSH, HOST_USER, pkey=RSA_KEY, timeout=15)
        SSH.exec_command(command)
        SSH.close()
        return True, 'OK'
    except (socket.error, paramiko.ssh_exception.BadHostKeyException, paramiko.ssh_exception.AuthenticationException, paramiko.ssh_exception.SSHException) as e:
        SSH.close()
        err_mes = str(type(e)) + '\n' + str(e)
        return False, err_mes

def check_and_post(order, complete, err_mes):
    if complete:
        slack_post(order + 'を実行しました')
    else:
        slack_post(order + 'の実行に失敗しました\n' + err_mes)

def on_connect(client, userdata, flags, respons_code):
    slack_post('接続に成功しました')
    client.subscribe(ADDRESS)

def on_message(client, userdata, msg):
    message = json.loads(msg.payload.decode('utf-8'))['data']
    if message == BOOTUP_WORD:
        send_magic_packet(MACADDR)
        slack_post('WOLを実行しました')
    elif message == SLEEP_WORD:
        complete, err_mes = ssh_exec(PSSD_PATH + ' -d -t 5')
        check_and_post('sleep', complete, err_mes)
    elif message == SLEEP_LATER_WORD:
        slack_post('60秒後にsleepを実行します')
        time.sleep(60)
        complete, err_mes = ssh_exec(PSSD_PATH + ' -d')
        check_and_post('sleep_later', complete, err_mes)
    elif message == SHUTDOWN_WORD:
        complete, err_mes = ssh_exec(PSSD_PATH)
        check_and_post('shutdown', complete, err_mes)
    elif message == SHUTDOWN_LATER_WORD:
        slack_post('60秒後にshutdownを実行します')
        time.sleep(60)
        complete, err_mes = ssh_exec(PSSD_PATH)
        check_and_post('shutdown_later', complete, err_mes)
    elif message == "PING":
        slack_post('pingを受け取りました')
    else:
        slack_post('メッセージが違います')


client = mqtt.Client()
client.username_pw_set("token:%s"%TOKEN)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(os.path.join(os.path.dirname(__file__), CACERT))
RSA_KEY = paramiko.RSAKey.from_private_key_file(KEY_FILE, PASSPHRASE)
SSH = paramiko.SSHClient()
SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOSTNAME, port=PORT, keepalive=60)
client.loop_forever()
