import pika
import json
import time
import requests
import threading

def initializeChannel(logger, pika_name, queue_name):
    credentials = pika.PlainCredentials(pika_name,pika_name)
    parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials, heartbeat=0, blocked_connection_timeout=3000)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.queue_declare(queue=queue_name,durable = True)
    channel.queue_purge(queue=queue_name)

    logger.info("Rabbitmq connections initialized ")

    return channel, connection

def get_message(channel, queue_name):   
    method_frame, _, recv = channel.basic_get(queue_name)
    if recv:
        print(recv)
        message = str(recv, 'utf-8')
        message = json.loads(message)
        return message
    return None

def send_alert(logger, message, vicki_app):

    payload = json.dumps(["createMachineAlert","CV:WARNING:"+message])
    headers = {'Content-Type': 'application/json'}
    logger.info(message)
    try:
        response = requests.request("POST", vicki_app, headers=headers, data=payload)    
        logger.info(response)
        if response.status_code == 200:
            logger.info('Sending alert - Success')
        else:
            logger.info('Sending alert - Failed')   
    except:
        logger.info('Sending alert - Failed')
        

    


def message_processing(logger, pika_name, queue_name, output_queue, vicki_app, minutes_to_end_transcation, warning_message_time,message_timeout):
    try:
        channel, connection = initializeChannel(logger, pika_name, queue_name)
    except:
        message = {'cmd': 'Stop'}
        output_queue.put(message)
        return 0
    
    try:
        last_message_time = time.time()
        door_opened_time = None
        door_locked_sent = False
        warning_sent = False

        while True:
            current_time = time.time()
            message = get_message(channel, queue_name)
            if message:
                last_message_time = current_time
                if message['cmd'] == "DoorOpened":
                    door_opened_time = current_time
                    door_locked_sent = False
                    warning_sent = False
                    output_queue.put(message)
                elif message['cmd'] == "DoorLocked":
                    if door_locked_sent:
                        pass
                    else:
                        door_opened_time = None
                        output_queue.put(message)
                elif message['cmd'] == "OrderSettled":
                    door_opened_time = None
                    output_queue.put(message)
                elif message['cmd'] == 'Technician':
                    door_opened_time = None
                    output_queue.put(message)
            elif current_time - last_message_time > message_timeout:
                last_message_time = current_time
                alert = 'Pipeline is not getting messages.'
                # alert_thread = threading.Thread(target=send_alert, args = (logger, alert, vicki_app))
                # alert_thread.start()
                # alert_thread.join()
                message = {'cmd': 'Stop'}
                output_queue.put(message)

            if door_opened_time:
                if current_time - door_opened_time > warning_message_time and not warning_sent:
                    message = 'Door opened but not locked within 3 minutes.'
                    threading.Thread(target=send_alert, args = (logger, message, vicki_app)).start()
                    #logger.info("Warning: Door opened but not locked within 3 minutes.")
                    warning_sent = True
                elif current_time - door_opened_time > minutes_to_end_transcation:
                    message = 'Door opened but not locked within 5 minutes. Generating DoorLocked message.'
                    threading.Thread(target=send_alert, args = (logger, message, vicki_app)).start()
                    #logger.info("Error: Door opened but not locked within 5 minutes. Generating 'DoorLocked' message.")
                    output_queue.put({'cmd': 'DoorLocked'})
                    door_locked_sent = True
                    door_opened_time = None
                    warning_sent = False

    except:
        if connection:
            connection.close()
        message = {'cmd': 'Stop'}
        output_queue.put(message)
        return 0