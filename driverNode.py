import asyncio
from kafka import KafkaConsumer, KafkaProducer
import sys
import hashlib
import random
from datetime import datetime
import json
import requests
import time
import statistics

kafkaIp, orchsIp = sys.argv[1:]
isTrigger = False

def uniqueHash():
    unique_identifier = random.randint(1, 10000)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    unique_string = f"{timestamp}-{unique_identifier}"
    unique_hash = hashlib.sha1(unique_string.encode()).hexdigest()[:8]
    return unique_hash

unique_hash = uniqueHash()

async def send_requests_with_delay(url, num_requests, delay_interval_seconds, test_id,test_type):
    response_times = []

    for i in range(num_requests):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()

        response_time = end_time - start_time
        response_times.append(response_time)

        print(f"Request {i + 1} Status Code: {response.status_code}, Response Time: {response_time:.2f} seconds")
        if test_type=='TSUNAMI' and  delay_interval_seconds:
            time.sleep(delay_interval_seconds)
        if sum(response_times)>=0.75:
            mean_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)

            producer.send('metrics', json.dumps({
                "metrics": {
                    "mean_latency": mean_response_time * 1000,
                    "median_latency": median_response_time * 1000,
                    "min_latency": min_response_time * 1000,
                    "max_latency": max_response_time * 1000,
                },
                "node_id": unique_hash,
                "test_id": test_id,
                "report_id": uniqueHash()
            }).encode('utf-8'))
            response_times = []
    

async def process_message(message):
    try:
        if message and message.value:
            ms = json.loads(message.value.decode('utf-8'))
            print(ms['test_id'])
            await send_requests_with_delay('https://www.google.com', int(ms['message_count_per_driver']), int(ms['test_message_delay']), ms['test_id'],ms['test_type'])
            producer.flush()
            # producer.send('metrics',b'EOFBREAK')
            return
        else:
            print("Received message with None value.")
    except Exception as e:
        print(f"Error processing message: {e}")

async def consumer_triggerr(consumer_trigger):
    global isTrigger
    for msgs in consumer_trigger:
        print("in trigger")
        msg_val = msgs.value.decode('utf-8')
        if msg_val == 'EOFBREAK':
            consumer_trigger.close()
            break
        msg_value = json.loads(msg_val)
        if msg_value["trigger"] == "YES":
            print('yes')
            isTrigger = True
            print(f"Received message: {msg_value}")
            return


async def consume_messages(consumer_Test_Conf):
    try:
        print('p')
        for message in consumer_Test_Conf:
            print('pout')
            await process_message(message)
            consumer_Test_Conf.close()
            print('sending break')
            producer.send('metrics',b'EOFBREAK')
            return
    except Exception as e:
        print(f"Error consuming messages: {e}")


async def main():
    print(unique_hash)
    producer.send('register', json.dumps({'node_id': unique_hash, 'node_IP': 'IPAddr', 'message_type': 'DRIVER_NODE_REGISTER'}).encode('utf-8'))
    task = asyncio.create_task(consumer_triggerr(consumer_trigger))
    task.add_done_callback(await consume_messages(consumer_Test_Conf))
    return

if __name__ == '__main__':
    producer = KafkaProducer(bootstrap_servers=[kafkaIp])
    consumer_Test_Conf = KafkaConsumer('test_config', group_id=f'{unique_hash}test', bootstrap_servers=[kafkaIp])
    consumer_trigger = KafkaConsumer('trigger', group_id=f'{unique_hash}trigger', bootstrap_servers=[kafkaIp])

    asyncio.run(main())