# Домашнее задание по лекции "Clickhouse"

## Задание

Необходимо, используя туториал https://clickhouse.tech/docs/ru/getting-started/tutorial/ :
- развернуть БД
- выполнить импорт тестовой БД
- выполнить несколько запросов и оценить скорость выполнения
- развернуть дополнительно одну из тестовых БД https://clickhouse.com/docs/en/getting-started/example-datasets , протестировать скорость запросов
- развернуть Кликхаус в кластерном исполнении, создать распределенную таблицу, заполнить данными и протестировать скорость по сравнению с 1 инстансом

## Выполнение задания:

Планирую настроить кластер Clickhouse в следующей конфигурации:
- сервер lab1: shard 1/replica 1 + 1-й узел Clickhouse Keeper
- сервер lab2: shard 1/replica 2 + 2-й узел Clickhouse Keeper
- сервер lab3: shard 2/replica 1 + 3-й узел Clickhouse Keeper
- сервер lab4: shard 2/replica 2 + 4-й узел Clickhouse Keeper

### Установка и настройка Clickhouse

На каждом сревере:

1. Подключаю репозиторий Clickhouse:
```
yum-config-manager --add-repo https://packages.clickhouse.com/rpm/clickhouse.repo
```

2. Устанавливаю необходимые пакеты Clickhouse:
```
yum install clickhouse-server clickhouse-client
```

3. Добавляю параметр принятия СУБД внешних запросв, создав файл /etc/clickhouse-server/config.d/listen_host.xml со следующим содержимым:
```
<clickhouse>

<listen_host>0.0.0.0</listen_host>

</clickhouse>
```

4. Включаю автозапуск сервиса clickhouse-server и запускаю его:
```
systemctl start clickhouse-server
systemctl start clickhouse-server
```

### Настройка кластера Clickhouse

На каждом сервере кластера:

1. Добавляю настроку нового кластера в файл конфигурации /etc/clickhouse-server/config.d/remote_server.xml со следующим содержанием:
```
<clickhouse>

<remote_servers>
    <test_cluster>
        <shard>
            <replica>
                <host>lab1</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>lab2</host>
                <port>9000</port>
            </replica>
        </shard>
        <shard>
            <replica>
                <host>lab3</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>lab4</host>
                <port>9000</port>
            </replica>
        </shard>
    </test_cluster>
</remote_servers>

</clickhouse>
```

2. Добавляю настройку Clickhouse Keeper в файл конфигурации /etc/clickhouse-server/config.d/keeper_server.xml со следующим содержимым (для первого узла:
```
<clickhouse>

<keeper_server>
    <tcp_port>2181</tcp_port>
    <server_id>1</server_id>
    <log_storage_path>/var/lib/clickhouse/coordination/log</log_storage_path>
    <snapshot_storage_path>/var/lib/clickhouse/coordination/snapshots</snapshot_storage_path>

    <coordination_settings>
        <operation_timeout_ms>10000</operation_timeout_ms>
        <session_timeout_ms>30000</session_timeout_ms>
        <raft_logs_level>trace</raft_logs_level>
    </coordination_settings>

    <raft_configuration>
        <server>
            <id>1</id>
            <hostname>lab1</hostname>
            <port>9444</port>
        </server>
        <server>
            <id>2</id>
            <hostname>lab2</hostname>
            <port>9444</port>
        </server>
        <server>
            <id>3</id>
            <hostname>lab3</hostname>
            <port>9444</port>
        </server>
        <server>
            <id>4</id>
            <hostname>lab4</hostname>
            <port>9444</port>
        </server>
    </raft_configuration>
</keeper_server>

</clickhouse>
```
ПРИМЕЧАНИЕ: параметр <server_id> на каждом сервере указывается свой, в соответсвии с прописанным <id> в <raft_configuration>.

3. Добавляю настройку макроса для создания таблиц в файл конфигурации /etc/clickhouse-server/config.d/macros.xml со следующим содержимым (для первого узла):
```
<clickhouse>

<macros>
    <shard>01</shard>
    <replica>01</replica>
</macros>

</clickhouse>
```
ПРИМЕЧАНИЕ: настройки <shard> и <replica> на каждом сервере свои, в соответсвии с прописанной в <remote_servers> ролью.

4. Перезапускаю сервис Clickhouse:
```
systemctl start clickhouse-server
```

5. Проверяю, что кластер появился в конфигурации:
```
lab2 :) select cluster, shard_num, replica_num, host_name, host_address from system.clusters where cluster = 'test_cluster';

SELECT
    cluster,
    shard_num,
    replica_num,
    host_name,
    host_address
FROM system.clusters
WHERE cluster = 'test_cluster'

Query id: 6070fd59-7d87-4609-9921-4e4161c6e6a7

   ┌─cluster──────┬─shard_num─┬─replica_num─┬─host_name─┬─host_address─┐
1. │ test_cluster │         1 │           1 │ lab1      │ 192.168.1.21 │
2. │ test_cluster │         1 │           2 │ lab2      │ 192.168.1.22 │
3. │ test_cluster │         2 │           1 │ lab3      │ 192.168.1.23 │
4. │ test_cluster │         2 │           2 │ lab4      │ 192.168.1.24 │
   └──────────────┴───────────┴─────────────┴───────────┴──────────────┘

4 rows in set. Elapsed: 0.001 sec.
```

6. Проверяю, что кластер Clickhouse Keeper запустился:
```
[root@lab4 ~]# echo srvr | nc localhost 2181
ClickHouse Keeper version: v24.9.2.42-stable-de7c791a2eadce4093409574d6560d2332b0dd18
Latency min/avg/max: 0/0/0
Received: 0
Sent: 0
Connections: 0
Outstanding: 0
Zxid: 0x
Mode: leader
Node count: 4
```
```
[root@lab2 ~]# echo stat | nc localhost 2181
ClickHouse Keeper version: v24.9.2.42-stable-de7c791a2eadce4093409574d6560d2332b0dd18
Clients:
 [::1]:35970(recved=0,sent=0)

Latency min/avg/max: 0/0/0
Received: 0
Sent: 0
Connections: 0
Outstanding: 0
Zxid: 0x
Mode: follower
Node count: 4
```

### Создание локальной БД и таблицы, и заполнение её данными

1. Создаю скрипт operations.sh для генерации CSV-файла данных для тестовой таблицы прихода/расхода денежных средстп по пользователям:
```
#!/bin/sh

NAMES=("Иван Иванов" "Пётр Петров" "Сидор Сидоров")  # массив с именами и фамилиями

for (( i=1; i <= 300000; i++ ))  # цикл с 300000 повторений
do
        NM=`tr -dc 0-2 </dev/urandom | head -c 1`  # генерация слуйчайного идентификатора в массиве имён и фамилий
        DT=`date +"%F %H:%M:00" --date="$i minutes ago"`  # генерация даты мотодом вычитания из текущей даты/времени минут, равных счётчику цикла
        OPER=`tr -dc 1-9 </dev/urandom | head -c 4`  # генерация случаной суммы операции
        OPER_1=`tr -dc 1-2 </dev/urandom | head -c 1`  # генерация знака операции (1 - положительный, 2 - отрицательный)
        if [[ $OPER_1 == "2" ]]  # добавление знака минус в операцию, в случае сгенерированного отрицательного знака
        then
                OPER="-$OPER"
        fi
        echo $i,$DT,${NAMES[$NM]},$OPER >> operations.csv  # запись строки данных в csv-файл
done
```

2. Создаю БД test:
```
lab1 :) CREATE DATABASE test;

CREATE DATABASE test

Query id: 308dd503-c87e-4aef-a596-a85f958e5549

Ok.

0 rows in set. Elapsed: 0.006 sec.
```

3. Создаю таблицу test.operations:
```
lab1 :) CREATE TABLE test.operations
(
oper_id Int32,
oper_dt DateTime,
oper_name String,
oper Int16
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(oper_dt)
ORDER BY (oper_id, oper_dt);

CREATE TABLE test.operations
(
    `oper_id` Int32,
    `oper_dt` DateTime,
    `oper_name` String,
    `oper` Int16
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(oper_dt)
ORDER BY (oper_id, oper_dt)

Query id: 7bc54efd-5441-49fb-9570-dcb1f175ed5e

Ok.

0 rows in set. Elapsed: 0.022 sec.
```

4. Загружаю в созданную таблицу сгенерированные в CSV-файле данные:
```
lab1 :) INSERT INTO test.operations FROM INFILE '/root/operations.csv' FORMAT CSV;

INSERT INTO test.operations FROM INFILE '/root/operations.csv' FORMAT CSV

Query id: f4a40354-7bff-46cb-b081-0221310edd7e

Ok.

300000 rows in set. Elapsed: 0.418 sec. Processed 300.00 thousand rows, 18.07 MB (717.55 thousand rows/s., 43.22 MB/s.)
Peak memory usage: 35.27 MiB.
```

