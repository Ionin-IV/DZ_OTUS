# Домашнее задание по лекции "Cassandra: System Components"

## Задание

Необходимо:
- Развернуть docker локально или в облаке.
- Поднять 3 узловый Cassandra кластер.
- Создать keyspase с 2-мя таблицами. Одна из таблиц должна иметь составной Partition key, как минимум одно поле - clustering key, как минимум одно поле не входящее в primiry key.
- Заполнить данными обе таблицы.
- Выполнить 2-3 варианта запроса использую WHERE.
- Создать вторичный индекс на поле, не входящее в primiry key.
- (*) нагрузить кластер при помощи Cassandra Stress Tool (используя "How to use Apache Cassandra Stress Tool.pdf" из материалов).

## Выполнение задания:

### Установка Cassandra и настройка кластера

1. Создаю три ВМ в конфигурации: 2 ядра процессора, 2 Гб памяти, 15 Гб жесткий диск, ОС CentOS 7.9

2. Устанавливаю требуемую версию JDK:
```
yum install java-11-openjdk
```

3. Устанавливаю заранее загруженные пакеты установки:
```
yum install cassandra-4.0.6-1.noarch.rpm  cassandra-tools-4.0.6-1.noarch.rpm
```

4. В файле конфигурации /etc/cassandra//conf/cassandra.yaml выставляю настройки кластера :
```
cluster_name: 'Test Cluster'
    - class_name: org.apache.cassandra.locator.SimpleSeedProvider
          - seeds: "192.168.1.21:7000,192.168.1.22:7000,192.168.1.23:7000"
listen_address: 192.168.1.2* # IP-адрес на каждом узле свой
```

5. Включаю и запускаю сервис cassandra:
```
systemctl enable cassandra
systemctl start cassandra
```

6. Проверяю, что кластер запустился и готов к работе:
```
[root@lab1 ~]# nodetool status
Datacenter: datacenter1
=======================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address       Load       Tokens  Owns (effective)  Host ID                               Rack
UN  192.168.1.23  69.06 KiB  16      71.8%             e64f49ac-332e-4ab0-af4c-0638454ab641  rack1
UN  192.168.1.22  69.06 KiB  16      61.3%             e2c72eb1-64ec-462f-be20-da5e859c4e0b  rack1
UN  192.168.1.21  69.05 KiB  16      66.9%             d8e2a3d1-4527-4892-a898-e61639bb3ea7  rack1
```


### Создание keyspace и таблиц

1. Создаю keyspace:
```
create keyspace test_keyspace with replication = { 'class' : 'SimpleStrategy', 'replication_factor' : 1};
```

2. Создаю таблицу операций прихода-расхода денежных стредств по нашим пользователям:
```
create table test_keyspace.operations_ru (
name varchar, -- имя пользователя
operDT timestamp, -- дата/время операции
oper int, -- приход/расход
operID int, -- ID операции
primary key (name, operDT) -- составной partition key по имени пользователя и дате/времени операции
)
with clustering order by (operDT asc); -- clustering key по дате/времени операции
```

3. Создаю таблицу операций прихода-расхода денежных стредств по иностранным пользователям:
```
create table test_keyspace.operations_en (
name varchar, -- имя пользователя
operID int, -- ID операции
oper int, -- приход/расход
operDT timestamp, -- дата/время операции
primary key (name, operID) -- составной partition key по имени пользователя и ID операции
)
with clustering order by (operID); -- clustering key по ID операции
```


### Наполнение таблиц данными

1. Создаю csv-файл operations_ru.csv с данными для таблицы операций прихода-расхода денежных стредств по нашим пользователям, запустив скрипт:
```
#!/bin/sh

NAMES=("Иван Иванов" "Пётр Петров" "Сидор Сидоров")  # массив с именами и фамилиями

for (( i=1; i <= 10000; i++ ))  # цикл с 10000 повторений
do
        NM=`tr -dc 0-2 </dev/urandom | head -c 1`  # генерация слуйчайного идентификатора в массиве имён и фамилий
        DT=`date +"%F %H:%M:00" --date="$i minutes ago"`  # генерация даты мотодом вычитания из текущей даты/времени минут, равных счётчику цикла
        OPER=`tr -dc 1-9 </dev/urandom | head -c 4`  # генерация случаной суммы операции
        OPER_1=`tr -dc 1-2 </dev/urandom | head -c 1`  # генерация знака операции (1 - положительный, 2 - отрицательный)
        if [[ $OPER_1 == "2" ]]  # добавление знака минус в операцию, в случае сгенерированного отрицательного знака
        then
                OPER="-$OPER"
        fi
        echo ${NAMES[$NM]},$DT,$OPER,$i >> operations_ru.csv  # запись строки данных в csv-файл
done
```

2. Загружаю данные в таблицу operations_ru:
```
cqlsh:test_keyspace> copy test_keyspace.operations_ru from '/root/operations_ru.csv' with delimiter = ',' and header = false;
Using 1 child processes

Starting copy of test_keyspace.operations_ru with columns [name, operdt, oper, operid].
Processed: 10000 rows; Rate:    5794 rows/s; Avg. rate:    9588 rows/s
10000 rows imported from 1 files in 0 day, 0 hour, 0 minute, and 1.043 seconds (0 skipped).
```

3. Создаю csv-файл operations_en.csv с данными для таблицы операций прихода-расхода денежных стредств по нашим пользователям, запустив скрипт:
```
#!/bin/sh

NAMES=("John Smith" "Fred Johnson" "Mike Jones")  # массив с именами и фамилиями

for (( i=1; i <= 10000; i++ ))  # цикл с 10000 повторений
do
        NM=`tr -dc 0-2 </dev/urandom | head -c 1`  # генерация слуйчайного идентификатора в массиве имён и фамилий
        DT=`date +"%F %H:%M:00" --date="$i minutes ago"`  # генерация даты мотодом вычитания из текущей даты/времени минут, равных счётчику цикла
        OPER=`tr -dc 1-9 </dev/urandom | head -c 4`  # генерация случаной суммы операции
        OPER_1=`tr -dc 1-2 </dev/urandom | head -c 1`  # генерация знака операции (1 - положительный, 2 - отрицательный)
        if [[ $OPER_1 == "2" ]]  # добавление знака минус в операцию, в случае сгенерированного отрицательного знака
        then
                OPER="-$OPER"
        fi
        echo ${NAMES[$NM]},$DT,$OPER,$i >> operations_en.csv  # запись строки данных в csv-файл
done
```

4. Загружаю данные в таблицу operations_en:
```
cqlsh:test_keyspace> copy test_keyspace.operations_en from '/root/operations_en.csv' with delimiter = ',' and header = false;
Using 1 child processes

Starting copy of test_keyspace.operations_en with columns [name, operid, oper, operdt].
Processed: 10000 rows; Rate:    7929 rows/s; Avg. rate:   12985 rows/s
10000 rows imported from 1 files in 0.770 seconds (0 skipped).
```


### Выполнение запросов к созданным таблицам

1. 
