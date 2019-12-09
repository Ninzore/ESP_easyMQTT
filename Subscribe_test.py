import paho.mqtt.client as client

server_address = '192.168.0.104'
port = 1883
topic = 'test'

def on_connect(client, userdata, flags, rc):
    '''callback when connected'''
    print("Connected with broker")
    client.subscribe(topic)
    client.publish(topic, payload='PC is Ready')


def on_message(client, userdata, message):
    '''callback when receive message'''
    print(str(message.payload))

client = client.Client(client_id="PC")
client.connect(server_address, port)
client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
