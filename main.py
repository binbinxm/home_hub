# coding=utf-8
# !/usr/bin/python3

import traceback
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

broker_URL = 'iot.binya.tech'
port = 1883

username = ''
password = ''
client_id = 'home_docker'
topic_up = '/home/env/up'
topic_down = '/home/env/down'

timestamp = str(time.time())

# ======================================================
isConnect = False
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

'''
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
'''

def func_arduino(ip, mac = ''):
    msg = {'message': 'device IP not found', 'status': 'fail'}
    try:
        if not ip == None:
            msg = requests.get('http://' + settings.arduino.ip + '/dht22', timeout = 5).json()['dht22']
    except Exception:
        traceback.print_exc()
    finally:
        return msg

def func_sp2_00(ip, mac):
    msg = {'message': 'device IP not found', 'status': 'fail'}
    try:
        if not ip == None:
            sp2_00 = broadlink.sp2(host=(settings.sp2_00.ip,80), mac=bytearray.fromhex(settings.sp2_00.mac.replace(':','')))
            sp2_00.auth()
            state = sp2_00.check_power()
            if state:
                msg = {'status':'succeed', 'message':'on'}
            else:
                msg = {'status':'succeed', 'message':'off'}
    except Exception:
        traceback.print_exc()
    finally:
        return msg

# =====================================================
if __name__ == '__main__':
    mqttc = mqtt.Client(client_id)
    #mqttc.username_pw_set(username, password)
    mqttc.username_pw_set('', '')
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_log = on_log

    mqttc.connect(broker_URL, port, 60)
    
    mqtt_thread = threading.Thread(target = mqttc.loop_forever)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    time.sleep(3)
    
    while(True):
        '''
        [settings.arduino.ip, settings.sp2_00.ip] = \
                ip_lookup([settings.arduino.mac, settings.sp2_00.mac])
        print([settings.arduino.ip, settings.sp2_00.ip])
        '''

        msg = {}
        msg['dht22'] = func_arduino(settings.arduino.ip, settings.arduino.mac)
        #msg['sp2_00'] = func_sp2_00(settings.sp2_00.ip, settings.sp2_00.mac)
        print(msg)

        ret= mqttc.publish(topic_up, json.dumps(msg))
        time.sleep(10)

