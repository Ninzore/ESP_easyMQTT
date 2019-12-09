import paho.mqtt.client as client
import paho.mqtt.publish as publish

server_address = 'localhost'
port = 1883
topic_1 = 'default'

def on_connect(client, userdata, flags, rc):
    '''callback when connected'''
    print("Connecting") 
    client.subscribe(topic_1)
    
def on_subscribe(client, userdata, mid, granted_qos):
    '''callback when subcribe to a topic'''
    print('Subcribe to topic ' +str(topic_1)) 
    client.publish(topic_1, payload = 'Publisher is ready') 

    
def on_message(client, userdata, message):
    '''callback when receive message'''
    print(str(message.payload)+' sent')
    content = input()
    publish.single(topic_1, payload = content)

client = client.Client()
client.connect(server_address, port)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe

client.loop_forever()