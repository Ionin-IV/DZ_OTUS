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
