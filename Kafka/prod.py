import json
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f'Ошибка доставки сообщения: {err}')
    else:
        print(f'Сообщение доставлено в {msg.topic()} [{msg.partition()}]')

topic = 'lab-py-topic'

f_json = open('/root/kafka_2.13-3.9.0/test.json')

data = json.load(f_json)

for line in data:

        producer.produce(topic, value=json.dumps(line), callback=delivery_report)

f_json.close()

producer.poll(0)
producer.flush()
