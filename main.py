# coding=utf-8
# !/usr/bin/python3

import datetime
import time
import hmac
import hashlib
import math
import threading
import requests
import json
import paho.mqtt.client as mqtt
from subprocess import check_output
import os
import settings
import broadlink
import keys

ProductKey = keys.ProductKey
ClientId = keys.ClientId  # 自定义clientId
DeviceName = keys.DeviceName
DeviceSecret = keys.DeviceSecret

broker_URL = ProductKey + ".iot-as-mqtt.cn-shanghai.aliyuncs.com"

topic_up = ProductKey + '/' + DeviceName + '/' + 'uplink'
topic_down = ProductKey + '/' + DeviceName + '/' + 'downlink'

# signmethod
signmethod = "hmacsha1"

# 当前时间毫秒值
us = math.modf(time.time())[0]
ms = int(round(us * 1000))
timestamp = str(ms)

data = "".join(("clientId", ClientId,\
        "deviceName", DeviceName,\
        "productKey", ProductKey,\
        "timestamp", timestamp\
        ))
print("data:", data)

if "hmacsha1" == signmethod:
    ret = hmac.new(\
            bytes(DeviceSecret, encoding="utf-8"),\
            bytes(data, encoding="utf-8"),\
            hashlib.sha1).hexdigest()
elif "hmacmd5" == signmethod:
    ret = hmac.new(\
            bytes(DeviceSecret, encoding="utf-8"),\
            bytes(data, encoding="utf-8"),\
            hashlib.md5).hexdigest()
else:
    raise ValueError

sign = ret
print("sign:", sign)

# ======================================================

strBroker = broker_URL
port = 1883

isConnect = False

client_id = "".join((ClientId,\
        "|securemode=3",\
        ",signmethod=", signmethod,\
        ",timestamp=", timestamp,\
        "|"))
username = "".join((DeviceName, "&", ProductKey))
password = sign

print("="*60)
print("client_id:", client_id)
print("username:", username)
print("password:", password)
print("="*60)

# ======================================================
def on_connect(mqttc, obj, flags, rc):
    print("OnConnetc, rc: " + str(rc))
    mqttc.subscribe(topic_down, 0)
    isConnect = True

def on_publish(mqttc, obj, msg):
    print("OnPublish, mid: " + str(msg))

def on_subscribe(mqttc, obj, msg, granted_qos):
    print("Subscribed: " + str(msg) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print("Log:" + string)

def on_message(mqttc, obj, msg):
    curtime = datetime.datetime.now()
    strcurtime = curtime.strftime("%Y-%m-%d %H:%M:%S")
    print(strcurtime + ": " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    on_exec(str(msg.payload))

def on_exec(strcmd):
    print("Exec:", strcmd)
    strExec = strcmd

# =====================================================

# =====================================================

def ip_lookup(mac_list):
    if type(mac_list) is not list:
        return None
    lines = check_output(['ip', 'n', 'show'])
    lines = lines.decode('utf-8')
    lines = lines.split('\n')
    ip = [None] * len(mac_list)
    for line in lines:
        for i in range(len(mac_list)):
            if mac_list[i] in line:
                tmp = line[0:line.find(' ')]
                if os.system('ping -c 1 ' + tmp) == 0:
                    ip[i] = tmp
    return ip


# =====================================================
if __name__ == '__main__':
    mqttc = mqtt.Client(client_id)
    mqttc.username_pw_set(username, password)
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_log = on_log

    mqttc.connect(strBroker, port, 120)
    
    mqtt_thread = threading.Thread(target = mqttc.loop_forever)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    time.sleep(3)
    
    while(True):
        [settings.arduino.ip, settings.sp2_00.ip] = \
                ip_lookup([settings.arduino.mac, settings.sp2_00.mac])
        print([settings.arduino.ip, settings.sp2_00.ip])
        
        msg = {}
        if settings.arduino.ip == None:
            msg['dht22'] = {'message': 'device IP not found', 'status': 'fail'}
        else:
            msg['dht22'] = requests.get('http://' + settings.arduino.ip).json()['dht22']
        
        if settings.sp2_00.ip == None:
            msg['sp2_00'] = {'message': 'device IP not found', 'status': 'fail'}
        else:
            sp2_00 = broadlink.sp2(host=(settings.sp2_00.ip,80), mac=bytearray.fromhex(settings.sp2_00.mac.replace(':','')))
            sp2_00.auth()
            state = sp2_00.check_power()
            if state:
                msg['sp2_00'] = {'status':'succeed', 'message':'on'}
            else:
                msg['sp2_00'] = {'status':'succeed', 'message':'off'}

        ret= mqttc.publish(topic_up, json.dumps(msg))
        print(msg)
        time.sleep(60)

