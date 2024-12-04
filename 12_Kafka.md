# Домашнее задание по лекции "Elasticsearch"

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

