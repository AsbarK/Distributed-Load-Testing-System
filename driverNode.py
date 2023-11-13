#!/usr/bin/env python3
from kafka import KafkaConsumer,KafkaProducer
import asyncio
import sys
import hashlib
import random
from datetime import datetime
import json
import requests
import time
import statistics

kafkaIp,orchsIp = sys.argv[1:]
def uniqueHash():
    unique_identifier = random.randint(1, 10000)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f') 
    unique_string = f"{timestamp}-{unique_identifier}"
    unique_hash = hashlib.sha1(unique_string.encode()).hexdigest()[:8]
    return unique_hash
unique_hash = uniqueHash()

def send_requests_with_delay(url, num_requests, delay_interval_seconds,test_id):
    response_times = []
    
    for i in range(num_requests):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        
        response_time = end_time - start_time
        response_times.append(response_time)
        
        print(f"Request {i + 1} Status Code: {response.status_code}, Response Time: {response_time:.2f} seconds")
        time.sleep(delay_interval_seconds) 

    mean_response_time = statistics.mean(response_times)
    median_response_time = statistics.median(response_times)
    min_response_time = min(response_times)
    max_response_time = max(response_times)
    # print(f"Mean Response Time: {mean_response_time:.2f} seconds")
    # print(f"Median Response Time: {median_response_time:.2f} seconds")
    # print(f"Minimum Response Time: {min_response_time:.2f} seconds")
    # print(f"Maximum Response Time: {max_response_time:.2f} seconds")
    producer.send('metrics', json.dumps({"metrics": {"mean_latency": mean_response_time * 1000,"median_latency": median_response_time * 1000,"min_latency": min_response_time * 1000,"max_latency": max_response_time * 1000,},"node_id": unique_hash,"test_id": test_id,"report_id": uniqueHash()}).encode('utf-8'))
async def process_message(message):
    try:
        if message and message.value:
            if(message.value.decode('utf-8') == 'EOFBREAK'):
                consumer_Test_Conf.close()
            ms = json.loads(message.value.decode('utf-8'))
            print(ms['test_id'])
            await send_requests_with_delay('https://www.google.com', 8, int(ms['test_message_delay']), ms['test_id'])
        else:
            print("Received message with None value.")
    except Exception as e:
        print(f"Error processing message: {e}")

async def consume_messages(consumer_Test_Conf):
    isTrigger = 0
    try:
        for message in consumer_Test_Conf:
            try:
                print("in trigger 0")
                for msgs in consumer_trigger:
                    print("in trigger")
                    msg_val = msgs.value.decode('utf-8')
                    if(msg_val == 'EOFBREAK'):
                        consumer_trigger.close()
                        break
                    msg_value = json.loads(msg_val)
                    if msg_value["trigger"] == "YES":
                        print('yes')
                        isTrigger = 1
                    print(f"Received message: {msg_value}")
            except KeyboardInterrupt:
                print('ex')
                pass
            if isTrigger:
                await process_message(message)
    except Exception as e:
        print(f"Error consuming messages: {e}")

consumer_Test_Conf = KafkaConsumer('test_config', group_id=f'{unique_hash}test', bootstrap_servers=[kafkaIp])
consumer_trigger = KafkaConsumer('trigger',group_id=f'{unique_hash}trigger', bootstrap_servers=[kafkaIp])
producer = KafkaProducer(bootstrap_servers=[kafkaIp])

async def main():
    await consume_messages(consumer_Test_Conf)

if __name__ == '__main__':
    print(unique_hash)
    producer.send('register',json.dumps({'node_id': unique_hash, 'node_IP': 'IPAddr', 'message_type': 'DRIVER_NODE_REGISTER'}).encode('utf-8'))
    # producer.send('register', b'EOF')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
