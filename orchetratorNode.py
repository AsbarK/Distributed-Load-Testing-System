#!/usr/bin/env python3
from kafka import KafkaConsumer,KafkaProducer
import asyncio
import hashlib
import random
from datetime import datetime
import json
def uniqueId():
    unique_identifier = random.randint(1, 10000)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f') 
    unique_string = f"{timestamp}-{unique_identifier}"
    unique_hash = hashlib.sha1(unique_string.encode()).hexdigest()[:8]
    return unique_hash

consumer_Register = KafkaConsumer('register', group_id='Register')
consumer_metrics = KafkaConsumer('metrics', group_id='metrics')
producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
rejisterd_DriverNodes = {}
metric_result = {}

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
            if node_id not in metric_result:
                metric_result[node_id] = {}
            metric_result[node_id][test_id] = metrics
            print({'node_id':node_id,'metrics':metrics,'test_id':test_id})
        else:
            print("Received empty or non-JSON message.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error processing message: {e}")

async def consume_messages_resigter(type_consumer,numberOfDriver,typeOfTopic,noTests):
    inde = 0
    if(typeOfTopic == 'register'):
        for message in type_consumer:
            await process_register_message(message)
            inde += 1
            if inde >= int(numberOfDriver):
                type_consumer.close()
                break
    elif(typeOfTopic == 'metrics'):
        coun = 0
        print(noTests)
        for message in type_consumer:
            await process_metric_message(message)
            coun += 1
            if coun >= (int(noTests)*  int(numberOfDriver)):
                type_consumer.close()
                break
# async def consume_messages_meteric():
async def main():
    numberOfTests = 0
    numberOfDriverNodes = input('Enter the number of Drivers:')
    await consume_messages_resigter(consumer_Register, numberOfDriverNodes, 'register',numberOfTests)
    while True:
        cmdInput = input("Enter a command (1 to send a message, exit to quit): ")
        if cmdInput == "1":
            producer.send('test_config', json.dumps({"test_id":uniqueId(),"test_type": "AVALANCHE","test_message_delay": "0"}).encode('utf-8'))
            numberOfTests+=1
        if cmdInput == "2":
            producer.send('test_config', json.dumps({"test_id":uniqueId(),"test_type": "TSUNAMI","test_message_delay": "10"}).encode('utf-8'))
            numberOfTests+=1
            
        elif cmdInput.lower() == "exit":
            producer.send('test_config', b'EOFBREAK')
            break
    await consume_messages_resigter(consumer_metrics, numberOfDriverNodes, 'metrics',numberOfTests)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print(rejisterd_DriverNodes,metric_result)
