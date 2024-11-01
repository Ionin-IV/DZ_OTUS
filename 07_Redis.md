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
- сервер lab1: master 192.168.1.21:7000, replica 192.168.1.21:7001
- сервер lab2: master 192.168.1.22:7000, replica 192.168.1.22:7001
- сервер lab3: master 192.168.1.23:7000, replica 192.168.1.23:7001

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
192.168.1.21:7000> cluster nodes
4e76bcdd078e00ea2df14712b1290bcdae5aaa61 192.168.1.23:7000 master - 0 1729598166451 3 connected 10923-16383
3b6f4abea55670f067f6262045e10d955db42508 192.168.1.21:7001 slave aaa2a6d95ac5f05f54779cc003d95394f999a446 0 1729598166351 4 connected
f8f98838a95da2acffb60327903b585c3ac4a2d0 192.168.1.23:7001 slave 4e76bcdd078e00ea2df14712b1290bcdae5aaa61 0 1729598166352 6 connected
aaa2a6d95ac5f05f54779cc003d95394f999a446 192.168.1.22:7000 master - 0 1729598165384 2 connected 5461-10922
bf4f2eb80aad547bccd6156aa69d34a76493a3fa 192.168.1.21:7000 myself,master - 0 0 1 connected 0-5460
c1b179c73eb2a8f85352bf7f049809714ed8d559 192.168.1.22:7001 slave bf4f2eb80aad547bccd6156aa69d34a76493a3fa 0 1729598167469 5 connected
```

12. Кластер создан и работает, но одна пара мастер-реплика создалась на одном сервере (192.168.1.23:7000 -> 192.168.1.23:7001), что не правильно в плане отказоустойчивости.
    Исправляю это, переподчиняя реплики со сдвигом вправо относительно мастеров (192.168.1.21:7000 -> 192.168.1.22:7001, 192.168.1.22:7000 -> 192.168.1.23:7001, 192.168.1.23:7000 -> 192.168.1.21:7001):
```
192.168.1.21:7001> CLUSTER REPLICATE 4e76bcdd078e00ea2df14712b1290bcdae5aaa61
OK

192.168.1.22:7001> CLUSTER REPLICATE bf4f2eb80aad547bccd6156aa69d34a76493a3fa
OK

192.168.1.23:7001> CLUSTER REPLICATE aaa2a6d95ac5f05f54779cc003d95394f999a446
OK
```

13. Теперь кластер собран правильно:
```
192.168.1.21:7000> cluster nodes
bf4f2eb80aad547bccd6156aa69d34a76493a3fa 192.168.1.21:7000 myself,master - 0 0 9 connected 0-5460
aaa2a6d95ac5f05f54779cc003d95394f999a446 192.168.1.22:7000 master - 0 1730454073297 2 connected 5461-10922
3b6f4abea55670f067f6262045e10d955db42508 192.168.1.21:7001 slave 4e76bcdd078e00ea2df14712b1290bcdae5aaa61 0 1730454073297 14 connected
c1b179c73eb2a8f85352bf7f049809714ed8d559 192.168.1.22:7001 slave bf4f2eb80aad547bccd6156aa69d34a76493a3fa 0 1730454072687 9 connected
f8f98838a95da2acffb60327903b585c3ac4a2d0 192.168.1.23:7001 slave aaa2a6d95ac5f05f54779cc003d95394f999a446 0 1730454072183 8 connected
4e76bcdd078e00ea2df14712b1290bcdae5aaa61 192.168.1.23:7000 master - 0 1730454072284 14 connected 10923-16383
```

### Тестирование загрузки разных структур данных

Для тестирования будет создан JSON-файл со следующей структурой:
- name - username пользователя
- data - данные пользователя
   - name - имя пользователя
   - age - возраст пользователя
   - post - номер поста пользователя
   - rating - рэйтинг пользователя

Создаю JSON-файл users.json следующим скриптом:
```
#!/bin/sh

NAMES=("Ivan" "Petr" "Pavel" "Dmitry" "Aleksey" "Sergey" "Vladimir" "Victor" "Oleg" "Andrey")

for (( i=1; i <= 10000; i++ ))
do
        NAME=`tr -dc 0-9 </dev/urandom | head -c 1`
        AGE=`tr -dc 1-9 </dev/urandom | head -c 2`
        POST=`tr -dc 1-9 </dev/urandom | head -c 3`
        RATING=$((10001-$i))

        echo { \"user\": \"user$i\", \"data\": { \"\name\": \"${NAMES[$NAME]}\", \"age\": \"$AGE\", \"post\": \"$POST\", \"rating\": \"$RATING\" } } >> users.json
done
```

Фрагмент сгенерированных данных:
```
{ "user": "user1", "data": { "name": "Ivan", "age": "78", "posts": "349", "rating": "10000" } }
{ "user": "user2", "data": { "name": "Sergey", "age": "88", "posts": "944", "rating": "9999" } }
{ "user": "user3", "data": { "name": "Aleksey", "age": "68", "posts": "634", "rating": "9998" } }
{ "user": "user4", "data": { "name": "Aleksey", "age": "32", "posts": "252", "rating": "9997" } }
{ "user": "user5", "data": { "name": "Sergey", "age": "56", "posts": "865", "rating": "9996" } }
```


#### Загрузка строк

1. Провожу парсинг JSON в файл со списком команд для Redis скриптом:
```
#!/bin/sh

while read JS; do

USER=`echo $JS | jq '.user' | sed 's/\"//g'`
NAME=`echo $JS | jq '.data.name' | sed 's/\"//g'`

echo SET user:$USER:name $NAME >> lines.txt

done <users.json
```
Фрагмент полученного файла:
```
SET user:user1:name Ivan
SET user:user2:name Sergey
SET user:user3:name Aleksey
SET user:user4:name Aleksey
SET user:user5:name Sergey
```

2. Провожу построчное выполнение команд из сгенерированного файла скриптом:
```
#!/bin/sh

while read COMM; do

redis-cli -c -h 192.168.1.21 -p 7000 $COMM

done <lines.txt
```
Время выполнения загрузки (время выполнения загрузки получаю командой time):
```
real    0m11.352s
user    0m4.505s
sys     0m5.218s
```

 3. Проверяю, что данные появились в БД:
```
192.168.1.21:7000> get user:user557:name
"Sergey"
```

4. Очищаю БД:
```
[root@lab1 ~]# redis-trib call 192.168.1.21:7000 FLUSHALL
>>> Calling FLUSHALL
192.168.1.21:7000: OK
192.168.1.22:7000: OK
192.168.1.21:7001: READONLY You can't write against a read only slave.
192.168.1.22:7001: READONLY You can't write against a read only slave.
192.168.1.23:7001: READONLY You can't write against a read only slave.
192.168.1.23:7000: OK
```


#### Загрузка Хэш-таблиц

1. Провожу парсинг JSON в файл со списком команд для Redis скриптом:
```
#!/bin/sh

while read JS; do

USER=`echo $JS | jq '.user' | sed 's/\"//g'`
NAME=`echo $JS | jq '.data.name' | sed 's/\"//g'`
AGE=`echo $JS | jq '.data.age' | sed 's/\"//g'`

echo HMSET $USER name $NAME age $AGE >> hset.txt

done <users.json
```
Фрагмент полученного файла:
```
HMSET user1 name Ivan age 78
HMSET user2 name Sergey age 88
HMSET user3 name Aleksey age 68
HMSET user4 name Aleksey age 32
HMSET user5 name Sergey age 56
```

2. Провожу построчное выполнение команд из сгенерированного файла скриптом:
```
#!/bin/sh

while read COMM; do

redis-cli -c -h 192.168.1.21 -p 7000 $COMM

done <hset.txt
```
Время выполнения загрузки:
```
real    0m11.672s
user    0m4.495s
sys     0m5.367s
```

3. Проверяю, что данные появились в БД:
```
192.168.1.21:7000> hgetall user992
1) "name"
2) "Vladimir"
3) "age"
4) "78"
```

4. Очищаю БД:
```
[root@lab1 ~]# redis-trib call 192.168.1.21:7000 FLUSHALL
>>> Calling FLUSHALL
192.168.1.21:7000: OK
192.168.1.22:7000: OK
192.168.1.21:7001: READONLY You can't write against a read only slave.
192.168.1.22:7001: READONLY You can't write against a read only slave.
192.168.1.23:7001: READONLY You can't write against a read only slave.
192.168.1.23:7000: OK
```


#### Загрузка упорядоченных множеств

1. Провожу парсинг JSON в файл со списком команд для Redis скриптом:
```
#!/bin/sh

while read JS; do

USER=`echo $JS | jq '.user' | sed 's/\"//g'`
RATING=`echo $JS | jq '.data.rating' | sed 's/\"//g'`

echo ZADD users:rating $RATING user:$USER >> zadd.txt

done <users.json
```
Фрагмент полученного файла:
```
ZADD users:rating 10000 user:user1
ZADD users:rating 9999 user:user2
ZADD users:rating 9998 user:user3
ZADD users:rating 9997 user:user4
ZADD users:rating 9996 user:user5
```

2. Провожу построчное выполнение команд из сгенерированного файла скриптом:
```
#!/bin/sh

while read COMM; do

redis-cli -c -h 192.168.1.21 -p 7000 $COMM

done <zadd.txt
```
Время выполнения загрузки:
```
real    0m12.429s
user    0m4.559s
sys     0m5.777s
```

3. Проверяю, что данные появились в БД:
```
192.168.1.22:7000> zrange users:rating 0 10
 1) "user:user10000"
 2) "user:user9999"
 3) "user:user9998"
 4) "user:user9997"
 5) "user:user9996"
 6) "user:user9995"
 7) "user:user9994"
 8) "user:user9993"
 9) "user:user9992"
10) "user:user9991"
11) "user:user9990"

192.168.1.22:7000> zrank users:rating user:user9993
(integer) 7
```

4. Очищаю БД:
```
[root@lab1 ~]# redis-trib call 192.168.1.21:7000 FLUSHALL
>>> Calling FLUSHALL
192.168.1.21:7000: OK
192.168.1.22:7000: OK
192.168.1.21:7001: READONLY You can't write against a read only slave.
192.168.1.22:7001: READONLY You can't write against a read only slave.
192.168.1.23:7001: READONLY You can't write against a read only slave.
192.168.1.23:7000: OK
```


#### Загрузка списков

1. Провожу парсинг JSON в файл со списком команд для Redis скриптом (т.к. user имеет по одному значению post, то списки формирую не по user, а по name):
```
#!/bin/sh

while read JS; do

NAME=`echo $JS | jq '.data.name' | sed 's/\"//g'`
POST=`echo $JS | jq '.data.posts' | sed 's/\"//g'`

echo RPUSH name:$NAME:posts post:$POST >> lists.txt

done <users.json
```
Фрагмент полученного файла:
```
RPUSH name:Ivan:posts post:349
RPUSH name:Sergey:posts post:944
RPUSH name:Aleksey:posts post:634
RPUSH name:Aleksey:posts post:252
RPUSH name:Sergey:posts post:865
```

2. Провожу построчное выполнение команд из сгенерированного файла скриптом:
```
#!/bin/sh

while read COMM; do

redis-cli -c -h 192.168.1.21 -p 7000 $COMM

done <lists.txt
```
Время выполнения загрузки:
```
real    0m12.593s
user    0m4.492s
sys     0m6.003s
```

3. Проверяю, что данные появились в БД:
```
192.168.1.21:7000> llen name:Ivan:posts
-> Redirected to slot [10382] located at 192.168.1.22:7000
(integer) 1037

192.168.1.22:7000> lrange name:Ivan:posts 0 10
 1) "post:349"
 2) "post:895"
 3) "post:977"
 4) "post:869"
 5) "post:313"
 6) "post:352"
 7) "post:732"
 8) "post:237"
 9) "post:473"
10) "post:743"
11) "post:586"
```

4. Очищаю БД:
```
[root@lab1 ~]# redis-trib call 192.168.1.21:7000 FLUSHALL
>>> Calling FLUSHALL
192.168.1.21:7000: OK
192.168.1.22:7000: OK
192.168.1.21:7001: READONLY You can't write against a read only slave.
192.168.1.22:7001: READONLY You can't write against a read only slave.
192.168.1.23:7001: READONLY You can't write against a read only slave.
192.168.1.23:7000: OK
```
