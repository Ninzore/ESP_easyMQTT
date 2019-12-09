import paho.mqtt.client as client
import paho.mqtt.publish as publish
import os
import re

server_address = '192.168.0.104'
port = 1883
topic_1 = 'test'
topic_2 = 'LED'

def on_connect(client, userdata, flags, rc):
    '''callback when connected'''
    print("Connecting") 
    client.subscribe(topic_1)
    
def on_subscribe(client, userdata, mid, granted_qos):
    '''callback when subcribe to a topic'''
    print('Subcribe to topic ' +str(topic_1))

def messageTopic1(client, userdata, message):
    '''callback when receive message'''
    print(str(message.payload))
    client.publish(topic_2, payload = message.payload)
    os.chdir('/home/pi/Desktop/MQTT_Test')
    file = open('test.txt', 'a')
    content = str(message.payload)
    pattern = re.compile(r'1.*')
    match = pattern.search(content)
    if match:
        file.write('LED ON\n')
        file.close
    
    else:
        file.write('LED OFF\n')
        file.close
    
client = client.Client()
client.connect(server_address, port)
client.on_connect = on_connect
client.on_message = messageTopic1
client.on_subscribe = on_subscribe

client.loop_forever()