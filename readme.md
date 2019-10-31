# wol_raspberrypi

ラズベリーパイで実行することを想定した、beebotteでメッセージを受け取ったらLAN内のPCをWOLで起動するためのPythonスクリプト

## Description
1. ラズベリーパイ側でwol.pyを実行してbeebotteを監視
2. 他の端末からbeebotteにHTTPリクエストでBOOTUP_WORDをPOSTする
3. wolが実行され、LAN内のPCが起動する
4. slackに通知が行く (wol_kai.pyのみ)

## Requirement
* sudo pip3 install wakeonlan
* sudo pip3 install paho-mqtt
* sudo pip3 install requests

## Usage
* BOOTUP_WORDをPOSTでWOL実行
* "PING"をPOSTでslackへのメッセージ通知のみ行う
