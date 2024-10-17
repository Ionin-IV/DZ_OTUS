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
ПРИМЕЧАНИЕ: параметр __server_id__ на каждом сервере указывается свой, в соответсвии с прописанным __id__ в __raft_configuration__.

3. Добавляю настройку макроса для создания таблиц в файл конфигурации /etc/clickhouse-server/config.d/macros.xml со следующим содержимым (для первого узла):
```
<clickhouse>

<macros>
    <shard>01</shard>
    <replica>01</replica>
</macros>

</clickhouse>
```
ПРИМЕЧАНИЕ: настройки __shard__ и __replica__ на каждом сервере свои, в соответсвии с прописанной в __remote_servers__ ролью.

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

### Создание БД и распределённой таблицы, и заполнение её данными

1. Создаю БД test_dist на всём кластере одной командой:
```
CREATE DATABASE test_dist ON CLUSTER test_cluster;

lab1 :) CREATE DATABASE test_dist ON CLUSTER test_cluster;

CREATE DATABASE test_dist ON CLUSTER test_cluster

Query id: 6761a793-49f4-450b-986c-6b725c6a971f

   ┌─host─┬─port─┬─status─┬─error─┬─num_hosts_remaining─┬─num_hosts_active─┐
1. │ lab2 │ 9000 │      0 │       │                   3 │                0 │
2. │ lab1 │ 9000 │      0 │       │                   2 │                0 │
3. │ lab4 │ 9000 │      0 │       │                   1 │                0 │
4. │ lab3 │ 9000 │      0 │       │                   0 │                0 │
   └──────┴──────┴────────┴───────┴─────────────────────┴──────────────────┘

4 rows in set. Elapsed: 0.067 sec.
```

2. Создаю локальные таблицы test_dist.operations_local на всём кластере однйо командой:
```
lab1 :) CREATE TABLE test_dist.operations_local ON CLUSTER test_cluster
(
oper_id Int32,
oper_dt DateTime,
oper_name String,
oper Int16
)
ENGINE = ReplicatedMergeTree('/test_cluster/tables/{shard}/operations_local','{replica}')
PARTITION BY toYYYYMM(oper_dt)
ORDER BY (oper_id, oper_dt);

CREATE TABLE test_dist.operations_local ON CLUSTER test_cluster
(
    `oper_id` Int32,
    `oper_dt` DateTime,
    `oper_name` String,
    `oper` Int16
)
ENGINE = ReplicatedMergeTree('/test_cluster/tables/{shard}/operations_local', '{replica}')
PARTITION BY toYYYYMM(oper_dt)
ORDER BY (oper_id, oper_dt)

Query id: bdc39839-9161-4c3b-b58c-cd4397c11c75

   ┌─host─┬─port─┬─status─┬─error─┬─num_hosts_remaining─┬─num_hosts_active─┐
1. │ lab2 │ 9000 │      0 │       │                   3 │                1 │
2. │ lab4 │ 9000 │      0 │       │                   2 │                1 │
3. │ lab1 │ 9000 │      0 │       │                   1 │                1 │
   └──────┴──────┴────────┴───────┴─────────────────────┴──────────────────┘
   ┌─host─┬─port─┬─status─┬─error─┬─num_hosts_remaining─┬─num_hosts_active─┐
4. │ lab3 │ 9000 │      0 │       │                   0 │                0 │
   └──────┴──────┴────────┴───────┴─────────────────────┴──────────────────┘

4 rows in set. Elapsed: 0.589 sec.
```

3. Создаю распределнноую таблицу test_dist.operations_dist:
```
lab1 :) CREATE TABLE test_dist.operations_dist ON CLUSTER test_cluster AS test_dist.operations_local
ENGINE = Distributed(test_cluster, test_dist, operations_local, rand());

CREATE TABLE test_dist.operations_dist ON CLUSTER test_cluster AS test_dist.operations_local
ENGINE = Distributed(test_cluster, test_dist, operations_local, rand())

Query id: 08f07aed-b7d0-4a7d-82c2-c4a83706d93b

   ┌─host─┬─port─┬─status─┬─error─┬─num_hosts_remaining─┬─num_hosts_active─┐
1. │ lab3 │ 9000 │      0 │       │                   3 │                1 │
2. │ lab4 │ 9000 │      0 │       │                   2 │                1 │
   └──────┴──────┴────────┴───────┴─────────────────────┴──────────────────┘
   ┌─host─┬─port─┬─status─┬─error─┬─num_hosts_remaining─┬─num_hosts_active─┐
3. │ lab2 │ 9000 │      0 │       │                   1 │                1 │
   └──────┴──────┴────────┴───────┴─────────────────────┴──────────────────┘
   ┌─host─┬─port─┬─status─┬─error─┬─num_hosts_remaining─┬─num_hosts_active─┐
4. │ lab1 │ 9000 │      0 │       │                   0 │                0 │
   └──────┴──────┴────────┴───────┴─────────────────────┴──────────────────┘

4 rows in set. Elapsed: 0.168 sec.
```

4. Копирую данные из ране заполненной локальной таблицы test.operations в распределённоую таблицу test_dist.operations_dist:
```
lab1 :) INSERT INTO test_dist.operations_dist SELECT * FROM test.operations;

INSERT INTO test_dist.operations_dist SELECT *
FROM test.operations

Query id: 3fb948ae-856c-4d6c-b125-78b01a2f04dd

Ok.

0 rows in set. Elapsed: 0.249 sec. Processed 300.00 thousand rows, 12.40 MB (1.20 million rows/s., 49.73 MB/s.)
Peak memory usage: 42.96 MiB.
```

### Тестирование и сравнение производительности запросов к локальной и распределённой таблицам

__ЗАПРОС №1__

Выполняю запрос суммы операций за сентябрь 2024 по именам пользователей на локальной таблице:
```
lab1 :) SELECT oper_name, sum(oper) FROM test.operations
WHERE oper_dt >= '2024-09-01 00:00:00' AND oper_dt < '2024-10-01 00:00:00'
GROUP BY oper_name
ORDER BY oper_name;

SELECT
    oper_name,
    sum(oper)
FROM test.operations
WHERE (oper_dt >= '2024-09-01 00:00:00') AND (oper_dt < '2024-10-01 00:00:00')
GROUP BY oper_name
ORDER BY oper_name ASC

Query id: 0a4c9fa5-336a-4453-b368-abbac227bf0a

   ┌─oper_name─────┬─sum(oper)─┐
1. │ Иван Иванов   │   -779279 │
2. │ Пётр Петров   │     25695 │
3. │ Сидор Сидоров │    607835 │
   └───────────────┴───────────┘

3 rows in set. Elapsed: 0.018 sec. Processed 43.23 thousand rows, 1.61 MB (2.36 million rows/s., 88.10 MB/s.)
Peak memory usage: 47.57 KiB.
```

Тот же запрос на распределённой таблице:
```
lab1 :) SELECT oper_name, sum(oper) FROM test_dist.operations_dist
WHERE oper_dt >= '2024-09-01 00:00:00' AND oper_dt < '2024-10-01 00:00:00'
GROUP BY oper_name
ORDER BY oper_name;

SELECT
    oper_name,
    sum(oper)
FROM test_dist.operations_dist
WHERE (oper_dt >= '2024-09-01 00:00:00') AND (oper_dt < '2024-10-01 00:00:00')
GROUP BY oper_name
ORDER BY oper_name ASC

Query id: 09ed66ed-a8a0-4240-9524-295391464be9

   ┌─oper_name─────┬─sum(oper)─┐
1. │ Иван Иванов   │   -779279 │
2. │ Пётр Петров   │     25695 │
3. │ Сидор Сидоров │    607835 │
   └───────────────┴───────────┘

3 rows in set. Elapsed: 0.010 sec. Processed 43.23 thousand rows, 1.61 MB (4.39 million rows/s., 163.83 MB/s.)
Peak memory usage: 419.00 KiB.
```

__РЕЗУЛЬТАТ__: запрос на распределённой таблице выполнился быстрее (0.010 sec против 0.018 sec).

__ЗАПРОС №2__

Выполняю запрос суммы операций прихода пользователя Иван Иванов по часам за 1 октября 2024 на локальной таблице:
```
lab1 :) SELECT toStartOfHour(oper_dt) AS h, sum(oper) AS s FROM test.operations
WHERE oper_dt >= '2024-10-01 00:00:00' AND oper_dt < '2024-10-02 00:00:00'
AND oper_name = 'Иван Иванов' AND oper > 0
GROUP BY h
ORDER BY h;

SELECT
    toStartOfHour(oper_dt) AS h,
    sum(oper) AS s
FROM test.operations
WHERE (oper_dt >= '2024-10-01 00:00:00') AND (oper_dt < '2024-10-02 00:00:00') AND (oper_name = 'Иван Иванов') AND (oper > 0)
GROUP BY h
ORDER BY h ASC

Query id: c63d2ba2-e8d5-4978-8949-7e190a3253cf

    ┌───────────────────h─┬─────s─┐
 1. │ 2024-10-01 00:00:00 │ 46680 │
 2. │ 2024-10-01 01:00:00 │ 46460 │
 3. │ 2024-10-01 02:00:00 │ 52465 │
 4. │ 2024-10-01 03:00:00 │ 56523 │
 5. │ 2024-10-01 04:00:00 │ 89934 │
 6. │ 2024-10-01 05:00:00 │ 34510 │
 7. │ 2024-10-01 06:00:00 │ 47156 │
 8. │ 2024-10-01 07:00:00 │ 37654 │
 9. │ 2024-10-01 08:00:00 │ 85987 │
10. │ 2024-10-01 09:00:00 │ 98349 │
11. │ 2024-10-01 10:00:00 │ 93401 │
12. │ 2024-10-01 11:00:00 │ 34632 │
13. │ 2024-10-01 12:00:00 │ 48253 │
14. │ 2024-10-01 13:00:00 │ 58466 │
15. │ 2024-10-01 14:00:00 │ 84087 │
16. │ 2024-10-01 15:00:00 │ 60157 │
17. │ 2024-10-01 16:00:00 │ 77111 │
18. │ 2024-10-01 17:00:00 │ 37586 │
19. │ 2024-10-01 18:00:00 │ 54536 │
20. │ 2024-10-01 19:00:00 │ 34471 │
21. │ 2024-10-01 20:00:00 │ 57108 │
22. │ 2024-10-01 21:00:00 │ 34727 │
23. │ 2024-10-01 22:00:00 │ 47264 │
24. │ 2024-10-01 23:00:00 │ 86117 │
    └─────────────────────┴───────┘

24 rows in set. Elapsed: 0.004 sec. Processed 22.78 thousand rows, 304.54 KB (6.27 million rows/s., 83.82 MB/s.)
Peak memory usage: 43.66 KiB.
```

Тот же запрос на распределённой таблице:
```
lab1 :) SELECT toStartOfHour(oper_dt) AS h, sum(oper) AS s FROM test_dist.operations_dist
WHERE oper_dt >= '2024-10-01 00:00:00' AND oper_dt < '2024-10-02 00:00:00'
AND oper_name = 'Иван Иванов' AND oper > 0
GROUP BY h
ORDER BY h;

SELECT
    toStartOfHour(oper_dt) AS h,
    sum(oper) AS s
FROM test_dist.operations_dist
WHERE (oper_dt >= '2024-10-01 00:00:00') AND (oper_dt < '2024-10-02 00:00:00') AND (oper_name = 'Иван Иванов') AND (oper > 0)
GROUP BY h
ORDER BY h ASC

Query id: aab603d2-c44d-4156-ada2-01617a5c42bd

    ┌───────────────────h─┬─────s─┐
 1. │ 2024-10-01 00:00:00 │ 46680 │
 2. │ 2024-10-01 01:00:00 │ 46460 │
 3. │ 2024-10-01 02:00:00 │ 52465 │
 4. │ 2024-10-01 03:00:00 │ 56523 │
 5. │ 2024-10-01 04:00:00 │ 89934 │
 6. │ 2024-10-01 05:00:00 │ 34510 │
 7. │ 2024-10-01 06:00:00 │ 47156 │
 8. │ 2024-10-01 07:00:00 │ 37654 │
 9. │ 2024-10-01 08:00:00 │ 85987 │
10. │ 2024-10-01 09:00:00 │ 98349 │
11. │ 2024-10-01 10:00:00 │ 93401 │
12. │ 2024-10-01 11:00:00 │ 34632 │
13. │ 2024-10-01 12:00:00 │ 48253 │
14. │ 2024-10-01 13:00:00 │ 58466 │
15. │ 2024-10-01 14:00:00 │ 84087 │
16. │ 2024-10-01 15:00:00 │ 60157 │
17. │ 2024-10-01 16:00:00 │ 77111 │
18. │ 2024-10-01 17:00:00 │ 37586 │
19. │ 2024-10-01 18:00:00 │ 54536 │
20. │ 2024-10-01 19:00:00 │ 34471 │
21. │ 2024-10-01 20:00:00 │ 57108 │
22. │ 2024-10-01 21:00:00 │ 34727 │
23. │ 2024-10-01 22:00:00 │ 47264 │
24. │ 2024-10-01 23:00:00 │ 86117 │
    └─────────────────────┴───────┘

24 rows in set. Elapsed: 0.061 sec. Processed 22.78 thousand rows, 850.82 KB (372.91 thousand rows/s., 13.93 MB/s.)
Peak memory usage: 411.72 KiB.
```

__РЕЗУЛЬТАТ__: запрос на распределённой таблице выполнялся значительно дольше, чем на локальной (0.061 sec против 0.004 sec).
__ПРЕДПОЛОЖЕНИЕ__: возможно, что при запросе относительно небольшого количества данных, накладные расходы отработки его на кластере перевешивают преимущества распределённой обработки запроса.
Проверю это в запросе №3.

__ЗАПРОС №3__

Выполняю запрос суммы операций прихода пользователя Иван Иванов по дням за сентябрь 2024 на локальной таблице:
```
lab1 :) SELECT toStartOfDay(oper_dt) AS h, sum(oper) AS s FROM test.operations
WHERE oper_dt >= '2024-09-01 00:00:00' AND oper_dt < '2024-10-01 00:00:00'
AND oper_name = 'Иван Иванов' AND oper > 0
GROUP BY h
ORDER BY h;

SELECT
    toStartOfDay(oper_dt) AS h,
    sum(oper) AS s
FROM test.operations
WHERE (oper_dt >= '2024-09-01 00:00:00') AND (oper_dt < '2024-10-01 00:00:00') AND (oper_name = 'Иван Иванов') AND (oper > 0)
GROUP BY h
ORDER BY h ASC

Query id: 5b7e217b-d40b-4cd1-8fd8-2c95d21a9c1c

    ┌───────────────────h─┬───────s─┐
 1. │ 2024-09-01 00:00:00 │ 1387048 │
 2. │ 2024-09-02 00:00:00 │ 1354309 │
 3. │ 2024-09-03 00:00:00 │ 1400067 │
 4. │ 2024-09-04 00:00:00 │ 1278262 │
 5. │ 2024-09-05 00:00:00 │ 1292971 │
 6. │ 2024-09-06 00:00:00 │ 1247133 │
 7. │ 2024-09-07 00:00:00 │ 1365794 │
 8. │ 2024-09-08 00:00:00 │ 1250538 │
 9. │ 2024-09-09 00:00:00 │ 1416730 │
10. │ 2024-09-10 00:00:00 │ 1267046 │
11. │ 2024-09-11 00:00:00 │ 1322078 │
12. │ 2024-09-12 00:00:00 │ 1302815 │
13. │ 2024-09-13 00:00:00 │ 1291035 │
14. │ 2024-09-14 00:00:00 │ 1323629 │
15. │ 2024-09-15 00:00:00 │ 1322617 │
16. │ 2024-09-16 00:00:00 │ 1212639 │
17. │ 2024-09-17 00:00:00 │ 1240230 │
18. │ 2024-09-18 00:00:00 │ 1480724 │
19. │ 2024-09-19 00:00:00 │ 1311580 │
20. │ 2024-09-20 00:00:00 │ 1295839 │
21. │ 2024-09-21 00:00:00 │ 1396495 │
22. │ 2024-09-22 00:00:00 │ 1430717 │
23. │ 2024-09-23 00:00:00 │ 1349871 │
24. │ 2024-09-24 00:00:00 │ 1385369 │
25. │ 2024-09-25 00:00:00 │ 1372300 │
26. │ 2024-09-26 00:00:00 │ 1291704 │
27. │ 2024-09-27 00:00:00 │ 1443136 │
28. │ 2024-09-28 00:00:00 │ 1167226 │
29. │ 2024-09-29 00:00:00 │ 1237934 │
30. │ 2024-09-30 00:00:00 │ 1292182 │
    └─────────────────────┴─────────┘

30 rows in set. Elapsed: 0.006 sec. Processed 43.23 thousand rows, 1.61 MB (6.83 million rows/s., 254.75 MB/s.)
Peak memory usage: 43.10 KiB.
```

Тот же запрос на распределённой таблице:
```
lab1 :) SELECT toStartOfDay(oper_dt) AS h, sum(oper) AS s FROM test_dist.operations_dist
WHERE oper_dt >= '2024-09-01 00:00:00' AND oper_dt < '2024-10-01 00:00:00'
AND oper_name = 'Иван Иванов' AND oper > 0
GROUP BY h
ORDER BY h;

SELECT
    toStartOfDay(oper_dt) AS h,
    sum(oper) AS s
FROM test_dist.operations_dist
WHERE (oper_dt >= '2024-09-01 00:00:00') AND (oper_dt < '2024-10-01 00:00:00') AND (oper_name = 'Иван Иванов') AND (oper > 0)
GROUP BY h
ORDER BY h ASC

Query id: c3840258-f962-4409-8671-8b0d81a8b921

    ┌───────────────────h─┬───────s─┐
 1. │ 2024-09-01 00:00:00 │ 1387048 │
 2. │ 2024-09-02 00:00:00 │ 1354309 │
 3. │ 2024-09-03 00:00:00 │ 1400067 │
 4. │ 2024-09-04 00:00:00 │ 1278262 │
 5. │ 2024-09-05 00:00:00 │ 1292971 │
 6. │ 2024-09-06 00:00:00 │ 1247133 │
 7. │ 2024-09-07 00:00:00 │ 1365794 │
 8. │ 2024-09-08 00:00:00 │ 1250538 │
 9. │ 2024-09-09 00:00:00 │ 1416730 │
10. │ 2024-09-10 00:00:00 │ 1267046 │
11. │ 2024-09-11 00:00:00 │ 1322078 │
12. │ 2024-09-12 00:00:00 │ 1302815 │
13. │ 2024-09-13 00:00:00 │ 1291035 │
14. │ 2024-09-14 00:00:00 │ 1323629 │
15. │ 2024-09-15 00:00:00 │ 1322617 │
16. │ 2024-09-16 00:00:00 │ 1212639 │
17. │ 2024-09-17 00:00:00 │ 1240230 │
18. │ 2024-09-18 00:00:00 │ 1480724 │
19. │ 2024-09-19 00:00:00 │ 1311580 │
20. │ 2024-09-20 00:00:00 │ 1295839 │
21. │ 2024-09-21 00:00:00 │ 1396495 │
22. │ 2024-09-22 00:00:00 │ 1430717 │
23. │ 2024-09-23 00:00:00 │ 1349871 │
24. │ 2024-09-24 00:00:00 │ 1385369 │
25. │ 2024-09-25 00:00:00 │ 1372300 │
26. │ 2024-09-26 00:00:00 │ 1291704 │
27. │ 2024-09-27 00:00:00 │ 1443136 │
28. │ 2024-09-28 00:00:00 │ 1167226 │
29. │ 2024-09-29 00:00:00 │ 1237934 │
30. │ 2024-09-30 00:00:00 │ 1292182 │
    └─────────────────────┴─────────┘

30 rows in set. Elapsed: 0.013 sec. Processed 43.23 thousand rows, 1.61 MB (3.27 million rows/s., 122.14 MB/s.)
Peak memory usage: 413.98 KiB.
```

__РЕЗУЛЬТАТ__: распределённый запрос хоть и не выполнился быстрее, и даже не сравнялся по времени, но всё равно время выполнения стало ощутимо меньше (0.013 sec против 0.006 sec).
__ВЫВОД__: предположение о зависимости скорости работы распределённого запроса от количества запрошенных данных, скорее всего, верное.
