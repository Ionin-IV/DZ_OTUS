# Домашнее задание по лекции "Kafka"

## Задание

1. Запустите Kafka (можно в docker)
2. Отправьте несколько сообщений используя утилиту kafka-producer
3. Прочитайте их, используя графический интерфейс или утилиту kafka-consumer
4. Отправьте и прочитайте сообщения программно - выберите знакомый язык программирования (C#, Java, Python или любой другой, для которого есть библиотека для работы с Kafka), отправьте и прочитайте несколько сообщений

Для пунктов 2 и 3 сделайте скриншоты отправки и получения сообщений.

Для пункта 4 приложите ссылку на репозитарий на гитхабе с исходным кодом.

## Выполнение задания

### Установка Kafka на ВМ

1. Скачиваю и распаковываю Kafka:
```
wget https://dlcdn.apache.org/kafka/3.9.0/kafka_2.13-3.9.0.tgz
tar -xzf kafka_2.13-3.9.0.tgz
cd kafka_2.13-3.9.0
```

2. Генерирую UUID кластера:
```
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
```

4. Форматирую директорию логов:
```
bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/kraft/reconfig-server.properties
```

5. Запускаю Kafka:
```
bin/kafka-server-start.sh config/kraft/reconfig-server.properties &
```

### Загрузка и получение данных стандартными утилитами Kafka

1. Создаю топик lap-topic с двумя партициями:
```
bin/kafka-topics.sh --create --topic lab-topic --partitions 2 --bootstrap-server localhost:9092
```

2. Запускаю в разных окнах продюсер и два консьюмера одинаковой группы:
```
bin/kafka-console-producer.sh --topic lab-topic --property "parse.key=true" --property "key.separator=:" --bootstrap-server localhost:9092

bin/kafka-console-consumer.sh --topic lab-topic --group consumer1 --from-beginning --bootstrap-server localhost:9092

bin/kafka-console-consumer.sh --topic lab-topic --group consumer1 --from-beginning --bootstrap-server localhost:9092
```

3. Отправляю в Kafka несколько пар "ключ:значение":
```
bin/kafka-console-producer.sh --topic lab-topic --property "parse.key=true" --property "key.separator=:" --bootstrap-server localhost:9092
>key1:val1
>key2:val2
>key3:val3
>key4:val4
>key5:val5
>key6:val6
>key7:val7
>key8:val8
>key9:val9
```

4. Получаю на двух консьюмерах данные с разных партиций:

Консьюмер 1:
```
bin/kafka-console-consumer.sh --topic lab-topic --group consumer1 --from-beginning --bootstrap-server localhost:9092
val2
val3
val4
val5
val7
val8
val9
```

Консьюмер 2:
```
bin/kafka-console-consumer.sh --topic lab-topic --group consumer1 --from-beginning --bootstrap-server localhost:9092
val1
val6
```

### Загрузка и получение данных программно

Для работы с данными выбираю скрипты, написанные на Python.

1. Создаю топик lab-py-topic:
```
bin/kafka-topics.sh --create --topic lab-py-topic --bootstrap-server localhost:9092
```

2. Создаю скрипт загрузки данных prod.py со следующим содержимым:
```
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
```

3. Создаю скрипт получения данных cons.py со следующим содержимым:
```
import json
from confluent_kafka import Consumer, KafkaException

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumer1',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)

topic = 'lab-py-topic'
consumer.subscribe([topic])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f'Конец раздела {msg.topic()} [{msg.partition()}]')
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            data = json.loads(msg.value().decode('utf-8'))
            print(f'Получено сообщение: {data}')
finally:
    consumer.close()
```

4. Для загрузки, создаю JSON-файл test.json со следующим содержимым:
```
[
{ "Key1": "Value1" },
{ "Key2": "Value2" },
{ "Key3": "Value3" }
]
```

5. В одном окне терминала запускаю срипт получения данных командой:
```
python3 cons.py
```

6. В другом окне терминала загружаю данные JSON-файла:
```
python3 prod.py
Сообщение доставлено в lab-py-topic [0]
Сообщение доставлено в lab-py-topic [0]
Сообщение доставлено в lab-py-topic [0]
```

7. Скрипт приёма данных получил их:
```
Получено сообщение: {'Key1': 'Value1'}
Получено сообщение: {'Key2': 'Value2'}
Получено сообщение: {'Key3': 'Value3'}
```

8. Перезапускаю скрипт приёма данных, и он опять получает те же данные, т.к. была выставлена настройка загрузки данных с начала ('auto.offset.reset': 'earliest'):
```
Получено сообщение: {'Key1': 'Value1'}
Получено сообщение: {'Key2': 'Value2'}
Получено сообщение: {'Key3': 'Value3'}
```

9. Меняю содержимое JSON-файла и отправляю его в Kafka:

Новое содержимое JSON-файла:
```
[
{ "Key4": "Value4" },
{ "Key5": "Value5" },
{ "Key6": "Value6" }
]
```

На стороне скрипта приёма добавились новые данные:
```
Получено сообщение: {'Key1': 'Value1'}
Получено сообщение: {'Key2': 'Value2'}
Получено сообщение: {'Key3': 'Value3'}
Получено сообщение: {'Key4': 'Value4'}
Получено сообщение: {'Key5': 'Value5'}
Получено сообщение: {'Key6': 'Value6'}
```

10. Останвливаю стрипт приёма данных, меняю в нём настройку старта получения данных на "latest", и запускаю скрипт снова. В этот раз старые данные не загружаются.

11. Меняю содержимое JSON-файла и отправляю его в Kafka:

Новое содержимое JSON-файла:
```
[
{ "Key7": "Value7" },
{ "Key8": "Value8" },
{ "Key9": "Value9" }
]
```

На стороне скрипта приёма появились только новые данные:
```
Получено сообщение: {'Key7': 'Value7'}
Получено сообщение: {'Key8': 'Value8'}
Получено сообщение: {'Key9': 'Value9'}
```
