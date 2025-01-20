# Домашнее задание по лекции "Облака"

## Задание

Необходимо:
 - одну из облачных БД заполнить данными (любыми из предыдущих дз);
 - протестировать скорость запросов.

Задание повышенной сложности*
сравнить 2-3 облачных NoSQL по скорости загрузки данных и времени выполнения запросов.

## Выполнение задания

### Создание тестовых данных для загрузки в БД

Создаю коллекцию operations прихода/расхода денежных средств со следующими полями:
* date - дата операции
* name - имя
* operation - приход/расход денежных средств (положительное число - приход, отрицательное - расход)

Для этого выполняю следующие действия:
1. Создаю нижеследующий скрипт (bash linux), генерирующий данные в json-файл для загрузки в БД:
```
#!/bin/sh

   NAMES=("Ivan" "Petr" "Pavel" "Dmitry" "Aleksey" "Sergey" "Vladimir" "Victor" "Oleg" "Andrey")  # массив с именами

for (( i=1; i <= 1000000; i++ ))  # цикл с 1000000 повторений
do
     NM=`tr -dc 0-9 </dev/urandom | head -c 1`  # генерация слуйчайного идентификатора в массиве имён
     DT=`date +"%F %H:%M:00" --date="$i minutes ago"`  # генерация даты мотодом вычитания из текущей даты/времени минут, равных счётчику цикла
     OPER=`tr -dc 1-9 </dev/urandom | head -c 4`  # генерация случаной суммы операции
     OPER_1=`tr -dc 1-2 </dev/urandom | head -c 1`  # генерация знака операции (1 - положительный, 2 - отрицательный)
     if [[ $OPER_1 == "2" ]]  # добавление знака минус в операцию, в случае сгенерированного отрицательного знака
     then
             OPER="-$OPER"
     fi
     echo { \"date\": \"$DT\", \"\name\": \"${NAMES[$NM]}\", \"operation\": { \"\$numberInt\": \"$OPER\"} } >> 1.json  # запись строки данных в json-файл
done
```

### Создание БД в Yandex Cloud

1. Регистрируюсь в Yandex Cloud.

2. Создаю кластер MongoDB с внешним доступом:

<kbd>![alt text](./16_Cloud/01.jpg)</kbd>

<kbd>![alt text](./16_Cloud/02.jpg)</kbd>

<kbd>![alt text](./16_Cloud/06.jpg)</kbd>

<kbd>![alt text](./16_Cloud/08.jpg)</kbd>

<kbd>![alt text](./16_Cloud/09.jpg)</kbd>

3. Добавляю в профиль безопасности внешний доступ к БД по порту 27018:

<kbd>![alt text](./16_Cloud/03.jpg)</kbd>

<kbd>![alt text](./16_Cloud/04.jpg)</kbd>

<kbd>![alt text](./16_Cloud/05.jpg)</kbd>

4. Копирую SSL-сертификат:

```
mkdir -p ~/.mongodb
wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" --output-document ~/.mongodb/root.crt
chmod 0644 ~/.mongodb/root.crt
```

5. Проверяю, что есть подключение к созданной БД с клиента на моём рабочем месте:

```
[root@host ~]# mongosh --norc --tls --tlsCAFile ~/.mongodb/root.crt --host 'rc1d-2rwigtopclqpgwnn.mdb.yandexcloud.net:27018' --username user1 --password '*****' db1
Current Mongosh Log ID: 67890ac1915396a22b544ca6
Connecting to:          mongodb://<credentials>@rc1d-2rwigtopclqpgwnn.mdb.yandexcloud.net:27018/db1?directConnection=true&tls=true&tlsCAFile=%2Froot%2F.mongodb%2Froot.crt&appName=mongosh+2.3.8
Using MongoDB:          7.0.5-mdb-c5ca57f0-sgn
Using Mongosh:          2.3.8

For mongosh info see: https://www.mongodb.com/docs/mongodb-shell/


To help improve our products, anonymous usage data is collected and sent to MongoDB periodically (https://www.mongodb.com/legal/privacy-policy).
You can opt-out by running the disableTelemetry() command.

------
   The server generated these startup warnings when booting
   2025-01-16T13:10:28.264+00:00: Using the XFS filesystem is strongly recommended with the WiredTiger storage engine. See http://dochub.mongodb.org/core/prodnotes-filesystem
------
```
