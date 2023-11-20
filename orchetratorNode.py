#!/usr/bin/env python3
import sys
from kafka import KafkaConsumer, KafkaProducer
import asyncio
import hashlib
import random
from datetime import datetime
import json
import time
import requests
import threading

num_drivers, test_type, delay, num_messages = sys.argv[1:]


def uniqueId():
    unique_identifier = random.randint(1, 10000)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    unique_string = f"{timestamp}-{unique_identifier}"
    unique_hash = hashlib.sha1(unique_string.encode()).hexdigest()[:8]
    return unique_hash


consumer_Register = KafkaConsumer('register', group_id='Register')
consumer_metrics = KafkaConsumer('metrics', group_id='metrics')
consumer_heartbeat = KafkaConsumer('heartbeat', group_id='heartbeat')
producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
rejisterd_DriverNodes = {}
metric_result = {}
temp_metric_result = {}


async def process_register_message(message):
    try:
        message_value = message.value.decode('utf-8')
        if message_value:
            msg = json.loads(message_value)
            rejisterd_DriverNodes[msg['node_id']] = msg
        else:
            print("Received empty or non-JSON message.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error processing message: {e}")


async def process_metric_message(message):
    try:
        message_value = message.value.decode('utf-8')
        if message_value:
            msg = json.loads(message_value)
            node_id = msg['node_id']
            test_id = str(msg['test_id'])
            metrics = msg['metrics']
            if node_id not in temp_metric_result:
                temp_metric_result[node_id] = {}
            temp_metric_result[node_id][test_id] = metrics
            print({'node_id': node_id, 'metrics': metrics, 'test_id': test_id})
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error processing message: {e}")


async def consume_messages_resigter(type_consumer, numberOfDriver, typeOfTopic, noTests):
    inde = 0
    if typeOfTopic == 'register':
        for message in type_consumer:
            await process_register_message(message)
            inde += 1
            if inde >= int(numberOfDriver):
                type_consumer.close()
                break
    elif typeOfTopic == 'metrics':
        inde = 0
        for message in type_consumer:
            if "EOFBREAK" in message.value.decode('utf-8'):
                inde+=1
                if inde >= (int(numberOfDriver)*noTests):
                    print('break')
                    type_consumer.close()
                    return
            await process_metric_message(message)


async def send_metrics_to_flask():
    while True:
        # Send temp_metric_result to Flask every one second
        await asyncio.sleep(1)
        if temp_metric_result:
            flask_app_url = 'http://127.0.0.1:5000/update_metrics'
            response = requests.post(flask_app_url, json={'metric_result': temp_metric_result})
            print("Temp metric results sent to Flask app")
            temp_metric_result.clear()

def run_asyncio():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_metrics_to_flask())

def run_main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

def consumer_heartBeat():
    for message in consumer_heartbeat:
        msg = message.value.decode('utf-8')
        if msg:
            msg_val = json.loads(msg)
            flask_app_url = 'http://127.0.0.1:5000/heartbeat'
            response = requests.post(flask_app_url, json={'heartbeat': msg_val})

async def main():
    numberOfTests = 0
    # numberOfDriverNodes = input('Enter the number of Drivers:')
    try:
        await consume_messages_resigter(consumer_Register, num_drivers, 'register', numberOfTests)

        test_id = uniqueId()
        producer.send('test_config', json.dumps({"test_id": test_id, "test_type": str(test_type),"test_message_delay": delay, "message_count_per_driver": num_messages}).encode('utf-8'))
        numberOfTests += 1
        # print('in trigger')
        producer.send('trigger', json.dumps({"test_id": test_id, "trigger": "YES"}).encode('utf-8'))
        producer.send('trigger', b'EOFBREAK')
        await consume_messages_resigter(consumer_metrics, num_drivers, 'metrics', numberOfTests),
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == '__main__':
    time.sleep(2 * int(num_drivers))

    thread1 = threading.Thread(target=run_asyncio)
    thread2 = threading.Thread(target=run_main)
    thread3 = threading.Thread(target=consumer_heartBeat)

    thread1.start()
    thread2.start()
    thread3.start()
    thread1.join()
    thread2.join()
    thread3.join()

    print(rejisterd_DriverNodes, metric_result)