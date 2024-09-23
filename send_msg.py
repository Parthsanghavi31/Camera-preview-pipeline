import pika
from utils import config  # Assuming you have a config file with necessary configurations
import logging  # Assuming logger is configured
import time
import json
Queue = config.Queue
def initializeChannel():
	#Initialize queue for door signal
	credentials = pika.PlainCredentials(config.pika_name,config.pika_name)
	parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials, heartbeat=0, blocked_connection_timeout=3000)

	connection = pika.BlockingConnection(parameters)
	channel = connection.channel()
	channel.queue_declare(queue=Queue,durable = True)

	#Clear queue for pre-existing messages
	channel.queue_purge(queue=Queue)

	print("Rabbitmq connections initialized ")
	return channel, connection


# Modify the `send_message()` function to accept the channel and connection parameters
def send_message(channel, connection, message):
    try:
        channel.basic_publish(exchange='',
                              routing_key=config.Queue,
                              body=json.dumps(message),
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # Make message persistent
                              ))
        print("Message sent successfully")
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        pass
for i in range(100):
    try:
        channel, connection = initializeChannel()

        # Message to send
        message_to_send = {
            "cmd": "DoorOpened",
            "parm1": str(i)+":True"  # Example parameters
        }

        message_to_send2 = {
            "cmd": "DoorLocked",
            "parm1": str(i)+":True"  # Example parameters
        }

        message_to_send1 = {
                "cmd": "OrderSettled",
                "parm1": str(i)+":"+str(i)
        }
        message_to_send3 = {'cmd': 'Technician', 'parm1':str(i+1)}

        send_message(channel, connection, message_to_send)

        time.sleep(15)
        send_message(channel, connection, message_to_send2)
        time.sleep(10)
        #send_message(channel, connection, message_to_send3)
        #time.sleep(10)
        send_message(channel, connection, message_to_send1)
        time.sleep(10)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the connection
        if connection is not None:
            connection.close()
