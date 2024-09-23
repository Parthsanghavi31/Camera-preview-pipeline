import pika
import json
from utils import config

def initializeChannel(pika_name, queue_name):
    credentials = pika.PlainCredentials(pika_name,pika_name)
    parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials, heartbeat=0, blocked_connection_timeout=3000)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.queue_declare(queue=queue_name,durable = True)
    channel.queue_purge(queue=queue_name)

    return channel, connection

def get_message(channel, queue_name):
   
    method_frame, _, recv = channel.basic_get(queue_name)
    if recv:
        #print(recv)
        message = str(recv, 'utf-8')
        message = json.loads(message)
        if message['cmd'] != "DoorOpened" and message['cmd'] != "OrderSettled" and message['cmd'] != "DoorLocked":
            return None
        else:
            return message

channel, connection = initializeChannel(config.pika_name, config.Queue)
while True:
    msg = get_message(channel, config.Queue)
    if msg != None:
        print(msg)
