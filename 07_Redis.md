# Домашнее задание по лекции "Redis"

## Задание

Необходимо:
- сохранить большой жсон (~20МБ) в виде разных структур - строка, hset, zset, list;
- протестировать скорость сохранения и чтения;
- предоставить отчет.

Задание повышенной сложности*
- настроить редис кластер на 3х нодах с отказоусточивостью, затюнить таймоуты

## Выполнение задания:

### Установка и настройка отказоустойчивого кластера Redis

Планирую настроить кластер Redis в конфигурации мастер и реплика на каждом узле:
- сервер lab1: master 192.168.1.21:7000 / replica 192.168.1.21:7001
- сервер lab2: master 192.168.1.22:7000 / replica 192.168.1.22:7001
- сервер lab3: master 192.168.1.23:7000 / replica 192.168.1.23:7001

1. Создаю три ВМ в конфигурации: 2 ядра процессора, 2 Гб памяти, 15 Гб жесткий диск, ОС CentOS 7.9

#### Далее на каждом сервере:

2. Устанавливаю необходимые пакеты:
```
yum install redis redis-trib
```

3. Создаю директории для файлов конфигурации и данных кластера:
```
mkdir -p /etc/redis/cluster
mkdir /etc/redis/cluster/7000
mkdir /var/lib/redis/7000
mkdir /etc/redis/cluster/7001
mkdir /var/lib/redis/7001
```

4. Создаю файл конфигурации мастера /etc/redis/cluster/7000/redis_7000.conf со следующим содержимым:
```
port 7000
dir /var/lib/redis/7000/
appendonly yes
protected-mode no
cluster-enabled yes
cluster-node-timeout 5000
cluster-config-file /etc/redis/cluster/7000/nodes_7000.conf
pidfile /var/run/redis/redis_7000.pid
logfile /var/log/redis/redis_7000.log
```

5. Создаю файл конфигурации реплики /etc/redis/cluster/7001/redis_7001.conf со следующим содержимым:
```
port 7001
dir /var/lib/redis/7001/
appendonly yes
protected-mode no
cluster-enabled yes
cluster-node-timeout 5000
cluster-config-file /etc/redis/cluster/7001/nodes_7001.conf
pidfile /var/run/redis/redis_7001.pid
logfile /var/log/redis/redis_7001.log
```

6. Выдаю необходимые права на директории:
```
chown redis:redis -R /var/lib/redis
chmod 770 -R /var/lib/redis
chown redis:redis -R /etc/redis
```

7. Создаю файл сервиса мастера /etc/systemd/system/redis_7000.service со следующим содержимым:
```
[Unit]
After=network.target
[Service]
ExecStart=/usr/bin/redis-server /etc/redis/cluster/7000/redis_7000.conf --supervised systemd
ExecStop=/bin/redis-cli -h 127.0.0.1 -p 7000 shutdown
Type=notify
User=redis
Group=redis
RuntimeDirectory=redis
RuntimeDirectoryMode=0755
LimitNOFILE=65535
[Install]
WantedBy=multi-user.target
```

8. Создаю файл сервиса мастера /etc/systemd/system/redis_7001.service со следующим содержимым:
```
[Unit]
After=network.target
[Service]
ExecStart=/usr/bin/redis-server /etc/redis/cluster/7001/redis_7001.conf --supervised systemd
ExecStop=/bin/redis-cli -h 127.0.0.1 -p 7001 shutdown
Type=notify
User=redis
Group=redis
RuntimeDirectory=redis
RuntimeDirectoryMode=0755
LimitNOFILE=65535
[Install]
WantedBy=multi-user.target
```

9. Включаю автозапуск настроенных сервисов и запускаю их:
```
systemctl enable redis_7000
systemctl start redis_7000
systemctl enable redis_7001
systemctl start redis_7001
```

10. Создаю кластер:
```
[root@lab1 ~]# redis-trib create --replicas 1 192.168.1.21:7000 192.168.1.22:7000 192.168.1.23:7000 192.168.1.21:7001 192.168.1.22:7001 192.168.1.23:7001
>>> Creating cluster
>>> Performing hash slots allocation on 6 nodes...
Using 3 masters:
192.168.1.21:7000
192.168.1.22:7000
192.168.1.23:7000
Adding replica 192.168.1.22:7001 to 192.168.1.21:7000
Adding replica 192.168.1.21:7001 to 192.168.1.22:7000
Adding replica 192.168.1.23:7001 to 192.168.1.23:7000
M: bf4f2eb80aad547bccd6156aa69d34a76493a3fa 192.168.1.21:7000
   slots:0-5460 (5461 slots) master
M: aaa2a6d95ac5f05f54779cc003d95394f999a446 192.168.1.22:7000
   slots:5461-10922 (5462 slots) master
M: 4e76bcdd078e00ea2df14712b1290bcdae5aaa61 192.168.1.23:7000
   slots:10923-16383 (5461 slots) master
S: 3b6f4abea55670f067f6262045e10d955db42508 192.168.1.21:7001
   replicates aaa2a6d95ac5f05f54779cc003d95394f999a446
S: c1b179c73eb2a8f85352bf7f049809714ed8d559 192.168.1.22:7001
   replicates bf4f2eb80aad547bccd6156aa69d34a76493a3fa
S: f8f98838a95da2acffb60327903b585c3ac4a2d0 192.168.1.23:7001
   replicates 4e76bcdd078e00ea2df14712b1290bcdae5aaa61
Can I set the above configuration? (type 'yes' to accept): yes
>>> Nodes configuration updated
>>> Assign a different config epoch to each node
>>> Sending CLUSTER MEET messages to join the cluster
Waiting for the cluster to join...
>>> Performing Cluster Check (using node 192.168.1.21:7000)
M: bf4f2eb80aad547bccd6156aa69d34a76493a3fa 192.168.1.21:7000
   slots:0-5460 (5461 slots) master
   1 additional replica(s)
M: 4e76bcdd078e00ea2df14712b1290bcdae5aaa61 192.168.1.23:7000
   slots:10923-16383 (5461 slots) master
   1 additional replica(s)
S: 3b6f4abea55670f067f6262045e10d955db42508 192.168.1.21:7001
   slots: (0 slots) slave
   replicates aaa2a6d95ac5f05f54779cc003d95394f999a446
S: f8f98838a95da2acffb60327903b585c3ac4a2d0 192.168.1.23:7001
   slots: (0 slots) slave
   replicates 4e76bcdd078e00ea2df14712b1290bcdae5aaa61
M: aaa2a6d95ac5f05f54779cc003d95394f999a446 192.168.1.22:7000
   slots:5461-10922 (5462 slots) master
   1 additional replica(s)
S: c1b179c73eb2a8f85352bf7f049809714ed8d559 192.168.1.22:7001
   slots: (0 slots) slave
   replicates bf4f2eb80aad547bccd6156aa69d34a76493a3fa
[OK] All nodes agree about slots configuration.
>>> Check for open slots...
>>> Check slots coverage...
[OK] All 16384 slots covered.
```

11. Проверяю, что кластер создан и работает:
```
[root@lab1 ~]# redis-cli -c -h 192.168.1.21 -p 7000
192.168.1.21:7000> cluster nodes
4e76bcdd078e00ea2df14712b1290bcdae5aaa61 192.168.1.23:7000 master - 0 1729598166451 3 connected 10923-16383
3b6f4abea55670f067f6262045e10d955db42508 192.168.1.21:7001 slave aaa2a6d95ac5f05f54779cc003d95394f999a446 0 1729598166351 4 connected
f8f98838a95da2acffb60327903b585c3ac4a2d0 192.168.1.23:7001 slave 4e76bcdd078e00ea2df14712b1290bcdae5aaa61 0 1729598166352 6 connected
aaa2a6d95ac5f05f54779cc003d95394f999a446 192.168.1.22:7000 master - 0 1729598165384 2 connected 5461-10922
bf4f2eb80aad547bccd6156aa69d34a76493a3fa 192.168.1.21:7000 myself,master - 0 0 1 connected 0-5460
c1b179c73eb2a8f85352bf7f049809714ed8d559 192.168.1.22:7001 slave bf4f2eb80aad547bccd6156aa69d34a76493a3fa 0 1729598167469 5 connected
```
