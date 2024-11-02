# Домашнее задание по лекции "DCS"

## Задание

- Разворачиваем кластер Etcd любым способом. Проверяем отказоустойчивость
- Разворачиваем кластер Consul любым способом. Проверяем отказоустойчивость


## Выполнение задания:

Для разворачивания и тестирования кластеров, создаю три ВМ в конфигурации: 2 ядра процессора, 2 Гб памяти, 15 Гб жесткий диск, ОС CentOS 7.9

### Разворачивание и тестирование кластера Etcd

1. На всех трёх серверах устанавливаю Etcd:
```
yum install etcd
```

2. На всех трёх серверах убираю конфигурационный файл по-умолчанию:
```
mv /etc/etcd/etcd.conf /etc/etcd/etcd.conf.def
```

3. На первом сервере создаю конфигурационный файл /etc/etcd/etcd.conf со следующим содержимым:
```
#[Member]
ETCD_DATA_DIR="/var/lib/etcd"
ETCD_LISTEN_PEER_URLS="http://192.168.1.21:2380"
ETCD_LISTEN_CLIENT_URLS="http://192.168.1.21:2379,http://127.0.0.1:2379"
ETCD_NAME="etcd1"
#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="http://192.168.1.21:2380"
ETCD_ADVERTISE_CLIENT_URLS="http://192.168.1.21:2379"
ETCD_INITIAL_CLUSTER="etcd1=http://192.168.1.21:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
ETCD_AUTO_COMPACTION_RETENTION="10"
ETCD_ENABLE_V2="true"
```

4. На первом сервере создаю конфигурационный файл сервиса /etc/systemd/system/etcd.service со следующим содержимым:
```
[Unit]
Description=etcd service
[Service]
Type=notify
User=etcd
ExecStart=/bin/etcd \
--name etcd1 \
--enable-v2=true \
--data-dir=/var/lib/etcd \
--initial-advertise-peer-urls http://192.168.1.21:2380 \
--listen-peer-urls http://192.168.1.21:2380 \
--listen-client-urls http://192.168.1.21:2379,http://127.0.0.1:2379 \
--advertise-client-urls http://192.168.1.21:2379 \
--initial-cluster-token etcd-cluster \
--initial-cluster etcd1=http://192.168.1.21:2380 \
--initial-cluster-state new
[Install]
WantedBy=multi-user.target
```

5. На первом сервере включаю и стартую сервис Etcd:
```
systemctl enable etcd
systemctl start etcd
```

6. Проверяю, что он добавлен в кластер:
```
[root@lab1 ~]# etcdctl member list
e57df09545f0deb9: name=etcd1 peerURLs=http://192.168.1.21:2380 clientURLs=http://192.168.1.21:2379 isLeader=true
```

7. На первом сервере добавляю втрой узел кластера:
```
[root@lab1 ~]# etcdctl member add etcd2 http://192.168.1.22:2380
Added member named etcd2 with ID dae98b5352f57d31 to cluster

ETCD_NAME="etcd2"
ETCD_INITIAL_CLUSTER="etcd2=http://192.168.1.22:2380,etcd1=http://192.168.1.21:2380"
ETCD_INITIAL_CLUSTER_STATE="existing"
```

8. На втором сервере создаю конфигурационный файл /etc/etcd/etcd.conf со следующим содержимым:
```
#[Member]
ETCD_DATA_DIR="/var/lib/etcd"
ETCD_LISTEN_PEER_URLS="http://192.168.1.22:2380"
ETCD_LISTEN_CLIENT_URLS="http://192.168.1.22:2379,http://127.0.0.1:2379"
ETCD_NAME="etcd2"
#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="http://192.168.1.22:2380"
ETCD_ADVERTISE_CLIENT_URLS="http://192.168.1.22:2379"
ETCD_INITIAL_CLUSTER="etcd1=http://192.168.1.21:2380,etcd2=http://192.168.1.22:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="existing"
ETCD_AUTO_COMPACTION_RETENTION="10"
ETCD_ENABLE_V2="true"
```

9. На втором сервере создаю конфигурационный файл сервиса /etc/systemd/system/etcd.service со следующим содержимым:
```
[Unit]
Description=etcd service
[Service]
Type=notify
User=etcd
ExecStart=/bin/etcd \
--name etcd2 \
--enable-v2=true \
--data-dir=/var/lib/etcd \
--initial-advertise-peer-urls http://192.168.1.22:2380 \
--listen-peer-urls http://192.168.1.22:2380 \
--listen-client-urls http://192.168.1.22:2379,http://127.0.0.1:2379 \
--advertise-client-urls http://192.168.1.22:2379 \
--initial-cluster-token etcd-cluster \
--initial-cluster etcd1=http://192.168.1.21:2380,etcd2=http://192.168.1.22:2380 \
--initial-cluster-state existing
[Install]
WantedBy=multi-user.target
```

10. На втором сервере включаю и стартую сервис Etcd:
```
systemctl enable etcd
systemctl start etcd
```

11. Проверяю, что он добавлен в кластер:
```
[root@lab2 ~]# etcdctl member list
dae98b5352f57d31: name=etcd2 peerURLs=http://192.168.1.22:2380 clientURLs=http://192.168.1.22:2379 isLeader=false
e57df09545f0deb9: name=etcd1 peerURLs=http://192.168.1.21:2380 clientURLs=http://192.168.1.21:2379 isLeader=true
```

12. На первом сервере добавляю третий узел кластера:
```
[root@lab1 ~]# etcdctl member add etcd3 http://192.168.1.23:2380
Added member named etcd3 with ID b677028a6445ff07 to cluster

ETCD_NAME="etcd3"
ETCD_INITIAL_CLUSTER="etcd3=http://192.168.1.23:2380,etcd2=http://192.168.1.22:2380,etcd1=http://192.168.1.21:2380"
ETCD_INITIAL_CLUSTER_STATE="existing"
```

13. На третьем сервере создаю конфигурационный файл /etc/etcd/etcd.conf со следующим содержимым:
```
#[Member]
ETCD_DATA_DIR="/var/lib/etcd"
ETCD_LISTEN_PEER_URLS="http://192.168.1.23:2380"
ETCD_LISTEN_CLIENT_URLS="http://192.168.1.23:2379,http://127.0.0.1:2379"
ETCD_NAME="etcd3"
#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="http://192.168.1.23:2380"
ETCD_ADVERTISE_CLIENT_URLS="http://192.168.1.23:2379"
ETCD_INITIAL_CLUSTER="etcd1=http://192.168.1.21:2380,etcd2=http://192.168.1.22:2380,etcd3=http://192.168.1.23:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="existing"
ETCD_AUTO_COMPACTION_RETENTION="10"
ETCD_ENABLE_V2="true"
```

14. На третьем сервере создаю конфигурационный файл сервиса /etc/systemd/system/etcd.service со следующим содержимым:
```
[Unit]
Description=etcd service
[Service]
Type=notify
User=etcd
ExecStart=/bin/etcd \
--name etcd3 \
--enable-v2=true \
--data-dir=/var/lib/etcd \
--initial-advertise-peer-urls http://192.168.1.23:2380 \
--listen-peer-urls http://192.168.1.23:2380 \
--listen-client-urls http://192.168.1.23:2379,http://127.0.0.1:2379 \
--advertise-client-urls http://192.168.1.23:2379 \
--initial-cluster-token etcd-cluster \
--initial-cluster etcd1=http://192.168.1.21:2380,etcd2=http://192.168.1.22:2380,etcd3=http://192.168.1.23:2380 \
--initial-cluster-state existing
[Install]
WantedBy=multi-user.target
```

15. На третьем сервере включаю и стартую сервис Etcd:
```
systemctl enable etcd
systemctl start etcd
```

16. Проверяю, что он добавлен в кластер:
```
[root@lab3 ~]# etcdctl member list
b677028a6445ff07: name=etcd3 peerURLs=http://192.168.1.23:2380 clientURLs=http://192.168.1.23:2379 isLeader=false
dae98b5352f57d31: name=etcd2 peerURLs=http://192.168.1.22:2380 clientURLs=http://192.168.1.22:2379 isLeader=false
e57df09545f0deb9: name=etcd1 peerURLs=http://192.168.1.21:2380 clientURLs=http://192.168.1.21:2379 isLeader=true
```

17. На первом и втором серверах редактирую в конфигурационном файле /etc/etcd/etcd.conf следующие параметры (на втором сервере только первый из них):
```
ETCD_INITIAL_CLUSTER="etcd1=http://192.168.1.21:2380,etcd2=http://192.168.1.22:2380,etcd3=http://192.168.1.23:2380"
ETCD_INITIAL_CLUSTER_STATE="existing"
```

18. На первом и втором серверах редактирую в конфигурационном файле сервиса /etc/systemd/system/etcd.service следующие параметры (на втором сервере только первый из них):
```
--initial-cluster etcd1=http://192.168.1.21:2380,etcd2=http://192.168.1.22:2380,etcd3=http://192.168.1.23:2380 \
--initial-cluster-state existing
```

19. На первом и втором серверах перечитываю конфигурации сервисов и перезапускаю сревис Etcd:
```
systemctl daemon-reload
systemctl restart etcd
```

20. Проверяю состояние кластера:
```
[root@lab1 ~]# etcdctl member list
b677028a6445ff07: name=etcd3 peerURLs=http://192.168.1.23:2380 clientURLs=http://192.168.1.23:2379 isLeader=true
dae98b5352f57d31: name=etcd2 peerURLs=http://192.168.1.22:2380 clientURLs=http://192.168.1.22:2379 isLeader=false
e57df09545f0deb9: name=etcd1 peerURLs=http://192.168.1.21:2380 clientURLs=http://192.168.1.21:2379 isLeader=false
```

21. Добавляю в кластер три ключа и проверяю, что они записались:
```
[root@lab1 ~]# etcdctl set key1 value1
value1
[root@lab1 ~]# etcdctl set key2 value2
value2
[root@lab1 ~]# etcdctl set key3 value3
value3

[root@lab1 ~]# etcdctl get key1
value1

[root@lab1 ~]# etcdctl ls
/key1
/key2
/key3
```

22. Останавливаю третий узел кластера, являющийся лидером на данный момент:
```
systemctl stop etcd
```

23. Проверяю, что лидер переключился:
```
[root@lab1 ~]# etcdctl member list
b677028a6445ff07: name=etcd3 peerURLs=http://192.168.1.23:2380 clientURLs=http://192.168.1.23:2379 isLeader=false
dae98b5352f57d31: name=etcd2 peerURLs=http://192.168.1.22:2380 clientURLs=http://192.168.1.22:2379 isLeader=false
e57df09545f0deb9: name=etcd1 peerURLs=http://192.168.1.21:2380 clientURLs=http://192.168.1.21:2379 isLeader=true
```

23. Проверяю, что данные всё так же доступны:
```
[root@lab1 ~]# etcdctl get key2
value2
```

24. Запускаю третий узел кластера:
```
systemctl start etcd
```

25. Теперь данные доступны и на третьем узле:
```
[root@lab3 ~]# etcdctl get key3
value3
```

