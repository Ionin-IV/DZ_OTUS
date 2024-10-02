# Домашнее задание по лекции "Оптимизация производительности mongodb"

## Задание

Необходимо:
- построить шардированный кластер из 3 кластерных нод( по 3 инстанса с репликацией) и с кластером конфига(3 инстанса);
- добавить балансировку, нагрузить данными, выбрать хороший ключ шардирования, посмотреть как данные перебалансируются между шардами;
- поронять разные инстансы, посмотреть, что будет происходить, поднять обратно. Описать что произошло.
- настроить аутентификацию и многоролевой доступ;

## Выполнение задания:

Для выполнения задания выбираю следующую конфигурацию:
- replica set конфигурации (мастер - реплика - реплика):
  * сервер lab1
  * сервер lab2
  * сервер lab3
- 1-я replica set (мастер - реплика - реплика):
  * сервер lab4
  * сервер lab5
  * сервер lab6
- 2-я replica set (мастер - реплика -реплика):
  * сервер lab7 (приоритет 100)
  * сервер lab8 (приоритет 90)
  * сервер lab9 (проиритет 80)
- 3-я replica set (мастер - реплика - реплика):
  * сервер lab10
  * сервер lab11
  * сервер lab12
- 1 сервер роутер mongos для работы с кластером:
  * сервер lab13

Примечание: во втором шарде сделаю сервера с прописанным приоритетом роли мастера.

### Установка ПО MongoDB

Устанавливаю ПО MongoDB по инструкции, описанной в предыдущем домашнем задании:
https://github.com/Ionin-IV/DZ_OTUS/blob/main/02_Mongo_1.md

### Создание replica set конфигурации

1. На каждом сервере конфигурации в файле /etc/mongod.conf меняю/добавляю следующие параметры:
```
net:
  port: 27019
  bindIp: 0.0.0.0

replication:
   replSetName: cfg_replica

sharding:
   clusterRole: configsvr
```

2. На каждом сервере конфигурации запускаю сервис mongod:
```
systemctl start mongod
```

3. На одном из серверов захожу в консоль:
```
mongosh --port 27019
```

4. Запускаю команду создания replica set конфигурации:
```
rs.initiate(
  {
    "_id": "cfg_replica",
    configsvr: true,
    members: [
      { "_id": 0, "host": "lab1:27019" },
      { "_id": 1, "host": "lab2:27019" },
      { "_id": 2, "host": "lab3:27019" }
    ]
  }
)
```

5. Запрашиваю конфигурацию созданной replica set:
```
cfg_replica [direct: primary] config> rs.conf()
{
  _id: 'cfg_replica',
  version: 1,
  term: 1,
  members: [
    {
      _id: 0,
      host: 'lab1:27019',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 1,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    },
    {
      _id: 1,
      host: 'lab2:27019',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 1,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    },
    {
      _id: 2,
      host: 'lab3:27019',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 1,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    }
  ],
  configsvr: true,
  protocolVersion: Long('1'),
  writeConcernMajorityJournalDefault: true,
  settings: {
    chainingAllowed: true,
    heartbeatIntervalMillis: 2000,
    heartbeatTimeoutSecs: 10,
    electionTimeoutMillis: 10000,
    catchUpTimeoutMillis: -1,
    catchUpTakeoverDelayMillis: 30000,
    getLastErrorModes: {},
    getLastErrorDefaults: { w: 1, wtimeout: 0 },
    replicaSetId: ObjectId('66f2c192d826ffeff5a2d64b')
  }
}
```

### Создание 1-й replica set

1. На каждом сервере в файле /etc/mongod.conf меняю/добавляю следующие параметры:
```
net:
  port: 27017
  bindIp: 0.0.0.0

replication:
   replSetName: shard01

sharding:
   clusterRole: shardsvr
```

2. На каждом сервере конфигурации запускаю сервис mongod:
```
systemctl start mongod
```

3. На одном из серверов захожу в консоль:
```
mongosh
```

4. Запускаю команду создания replica set конфигурации:
```
test> rs.initiate(
...   {
...     "_id": "shard01",
...     members: [
...       { "_id": 0, "host": "lab4:27017" },
...       { "_id": 1, "host": "lab5:27017" },
...       { "_id": 2, "host": "lab6:27017" }
...     ]
...   }
... )
{ ok: 1 }
```

5. Запрашиваю конфигурацию созданной replica set:
```
shard01 [direct: primary] test> rs.conf()
{
  _id: 'shard01',
  version: 1,
  term: 1,
  members: [
    {
      _id: 0,
      host: 'lab4:27017',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 1,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    },
    {
      _id: 1,
      host: 'lab5:27017',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 1,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    },
    {
      _id: 2,
      host: 'lab6:27017',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 1,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    }
  ],
  protocolVersion: Long('1'),
  writeConcernMajorityJournalDefault: true,
  settings: {
    chainingAllowed: true,
    heartbeatIntervalMillis: 2000,
    heartbeatTimeoutSecs: 10,
    electionTimeoutMillis: 10000,
    catchUpTimeoutMillis: -1,
    catchUpTakeoverDelayMillis: 30000,
    getLastErrorModes: {},
    getLastErrorDefaults: { w: 1, wtimeout: 0 },
    replicaSetId: ObjectId('66fbe922f841a3a7dbf77617')
  }
}
```

### Создание 2-й replica set

1. На каждом сервере в файле /etc/mongod.conf меняю/добавляю следующие параметры:
```
net:
  port: 27017
  bindIp: 0.0.0.0

replication:
   replSetName: shard02

sharding:
   clusterRole: shardsvr
```

2. На каждом сервере конфигурации запускаю сервис mongod:
```
systemctl start mongod
```

3. На одном из серверов захожу в консоль:
```
mongosh
```

4. Запускаю команду создания replica set конфигурации (с указанием приритетов роли мастера):
```
test> rs.initiate(
...   {
...     "_id": "shard02",
...     members: [
...       { "_id": 0, "host": "lab7:27017", "priority": 100 },
...       { "_id": 1, "host": "lab8:27017", "priority": 90 },
...       { "_id": 2, "host": "lab9:27017", "priority": 80 }
...     ]
...   }
... )
{ ok: 1 }
```

5. Запрашиваю конфигурацию созданной replica set:
```
shard02 [direct: primary] test> rs.conf()
{
  _id: 'shard02',
  version: 1,
  term: 2,
  members: [
    {
      _id: 0,
      host: 'lab7:27017',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 100,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    },
    {
      _id: 1,
      host: 'lab8:27017',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 90,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    },
    {
      _id: 2,
      host: 'lab9:27017',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 80,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    }
  ],
  protocolVersion: Long('1'),
  writeConcernMajorityJournalDefault: true,
  settings: {
    chainingAllowed: true,
    heartbeatIntervalMillis: 2000,
    heartbeatTimeoutSecs: 10,
    electionTimeoutMillis: 10000,
    catchUpTimeoutMillis: -1,
    catchUpTakeoverDelayMillis: 30000,
    getLastErrorModes: {},
    getLastErrorDefaults: { w: 1, wtimeout: 0 },
    replicaSetId: ObjectId('66fbe9b16409640653c55bb4')
  }
}
```

### Создание 3-й replica set

1. На каждом сервере в файле /etc/mongod.conf меняю/добавляю следующие параметры:
```
net:
  port: 27017
  bindIp: 0.0.0.0

replication:
   replSetName: shard03

sharding:
   clusterRole: shardsvr
```

2. На каждом сервере конфигурации запускаю сервис mongod:
```
systemctl start mongod
```

3. На одном из серверов захожу в консоль:
```
mongosh
```

4. Запускаю команду создания replica set конфигурации):
```
test> rs.initiate(
...   {
...     "_id": "shard03",
...     members: [
...       { "_id": 0, "host": "lab10:27017" },
...       { "_id": 1, "host": "lab11:27017" },
...       { "_id": 2, "host": "lab12:27017" }
...     ]
...   }
... )
{ ok: 1 }
```

5. Запрашиваю конфигурацию созданной replica set:
```
shard03 [direct: primary] test> rs.conf()
{
  _id: 'shard03',
  version: 4,
  term: 5,
  members: [
    {
      _id: 0,
      host: 'lab10:27017',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 1,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    },
    {
      _id: 1,
      host: 'lab11:27017',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 1,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    },
    {
      _id: 2,
      host: 'lab12:27017',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 1,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    }
  ],
  protocolVersion: Long('1'),
  writeConcernMajorityJournalDefault: true,
  settings: {
    chainingAllowed: true,
    heartbeatIntervalMillis: 2000,
    heartbeatTimeoutSecs: 10,
    electionTimeoutMillis: 10000,
    catchUpTimeoutMillis: -1,
    catchUpTakeoverDelayMillis: 30000,
    getLastErrorModes: {},
    getLastErrorDefaults: { w: 1, wtimeout: 0 },
    replicaSetId: ObjectId('66fbe9ec05c2775d0b25c10c')
  }
}
```

### Создание роутера mongos

1. Создаю файл /etc/systemd/system/mongos.service для запуска сервиса mogos со следующим содержимым:
```
[Unit]
Description=mongos
After=mongos.service

[Service]
ExecStart=/usr/bin/mongos -f /etc/mongos.conf
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Создаю файл /etc/mongos.conf со следующим содержимым:
```
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongos.log

net:
  port: 27017

sharding:
  configDB: cfg_replica/lab1:27019,lab2:27019,lab3:27019
```

3. Запускаю сервис mongos:
```
systemctl start mongos
```

4. Создаю 1-й шард:
```
sh.addShard("shard01/lab4:27017,lab5:27017,lab6:27017")

[direct: mongos] test> sh.addShard("shard01/lab4:27017,lab5:27017,lab6:27017")
{
  shardAdded: 'shard01',
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727349890, i: 4 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1727349890, i: 4 })
}
```

5. Создаю 2-й шард:
```
sh.addShard("shard02/lab7:27017,lab8:27017,lab9:27017")

[direct: mongos] test> sh.addShard("shard02/lab7:27017,lab8:27017,lab9:27017")
{
  shardAdded: 'shard02',
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727349931, i: 13 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1727349931, i: 3 })
}
```

6. Создаю 3-й шард:
```
sh.addShard("shard03/lab10:27017,lab11:27017,lab12:27017")

[direct: mongos] test> sh.addShard("shard03/lab10:27017,lab11:27017,lab12:27017")
{
  shardAdded: 'shard03',
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727351093, i: 4 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1727351093, i: 4 })
}
```

7. Проверяю состояние шардирования:
```
[direct: mongos] test> sh.status()
shardingVersion
{ _id: 1, clusterId: ObjectId('66fbe8e1a2cb1faac3912abb') }
---
shards
[
  {
    _id: 'shard01',
    host: 'shard01/lab4:27017,lab5:27017,lab6:27017',
    state: 1,
    topologyTime: Timestamp({ t: 1727785599, i: 2 })
  },
  {
    _id: 'shard02',
    host: 'shard02/lab7:27017,lab8:27017,lab9:27017',
    state: 1,
    topologyTime: Timestamp({ t: 1727785609, i: 2 })
  },
  {
    _id: 'shard03',
    host: 'shard03/lab10:27017,lab11:27017,lab12:27017',
    state: 1,
    topologyTime: Timestamp({ t: 1727785618, i: 2 })
  }
]
---
active mongoses
[ { '7.0.14': 1 } ]
---
autosplit
{ 'Currently enabled': 'yes' }
---
balancer
{
  'Currently running': 'no',
  'Failed balancer rounds in last 5 attempts': 0,
  'Currently enabled': 'yes',
  'Migration Results for the last 24 hours': { '6': 'Success' }
}
---
databases
[
  {
    database: { _id: 'config', primary: 'config', partitioned: true },
    collections: {
      'config.system.sessions': {
        shardKey: { _id: 1 },
        unique: false,
        balancing: true,
        chunkMetadata: [ { shard: 'shard01', nChunks: 1 } ],
        chunks: [
          { min: { _id: MinKey() }, max: { _id: MaxKey() }, 'on shard': 'shard01', 'last modified': Timestamp({ t: 1, i: 0 }) }
        ],
        tags: []
      }
    }
  },
  {
    database: {
      _id: 'test',
      primary: 'shard03',
      partitioned: false,
      version: {
        uuid: UUID('220c16b2-74cb-4abb-ba5a-01626b40b7fe'),
        timestamp: Timestamp({ t: 1727786816, i: 1 }),
        lastMod: 1
      }
    },
    collections: {
      'test.operations': {
        shardKey: { operID: 'hashed' },
        unique: false,
        balancing: true,
        chunkMetadata: [
          { shard: 'shard01', nChunks: 3 },
          { shard: 'shard02', nChunks: 3 },
          { shard: 'shard03', nChunks: 1 }
        ],
        chunks: [
          { min: { operID: MinKey() }, max: { operID: Long('-7534273545435840395') }, 'on shard': 'shard01', 'last modified': Timestamp({ t: 2, i: 0 }) },
          { min: { operID: Long('-7534273545435840395') }, max: { operID: Long('-5826499898353586714') }, 'on shard': 'shard02', 'last modified': Timestamp({ t: 3, i: 0 }) },
          { min: { operID: Long('-5826499898353586714') }, max: { operID: Long('-4117478068408228158') }, 'on shard': 'shard02', 'last modified': Timestamp({ t: 4, i: 0 }) },
          { min: { operID: Long('-4117478068408228158') }, max: { operID: Long('-2389961041160875228') }, 'on shard': 'shard01', 'last modified': Timestamp({ t: 5, i: 0 }) },
          { min: { operID: Long('-2389961041160875228') }, max: { operID: Long('-677797532829821895') }, 'on shard': 'shard02', 'last modified': Timestamp({ t: 6, i: 0 }) },
          { min: { operID: Long('-677797532829821895') }, max: { operID: Long('1067187518823003971') }, 'on shard': 'shard01', 'last modified': Timestamp({ t: 7, i: 0 }) },
          { min: { operID: Long('1067187518823003971') }, max: { operID: MaxKey() }, 'on shard': 'shard03', 'last modified': Timestamp({ t: 7, i: 1 }) }
        ],
        tags: []
      }
    }
  }
]
```

### Заполнение БД данными

Создаю коллекцию opaerations прихода/расхода денежных средств со следующими полями:
* operID - ID операции
* date - дата операции
* name - имя и фамилия
* operation - приход/расход денежных средств (положительное число - приход, отрицательное - расход)

Для этого выполняю следующие действия:
1. Создаю нижеследующий скрипт (bash linux), генерирующий данные в json-файл для загрузки в БД:
   ```
   #!/bin/sh

   NAMES=("Иван Иванов" "Пётр Петров" "Сидор Сидоров")  # массив с именами и фамилиями

   for (( i=1; i <= 100000; i++ ))  # цикл с 100000 повторений
   do
        NM=`tr -dc 0-2 </dev/urandom | head -c 1`  # генерация слуйчайного идентификатора в массиве имён и фамилий
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

2. Загружаю данные из сгенерированного json-файла в коллекцию operations БД test командой:
   ```
   mongoimport --db=test --collection=operations --file=1.json
   ```

### Шардирование коллекции

1. Создаю хэшированный индекс по полю operID:
```
[direct: mongos] test> db.operations.createIndex( { "operID" : "hashed" } )
operID_hashed
```

2. Шардирую коллекцию:
```
[direct: mongos] test> use admin
switched to db admin
[direct: mongos] admin> sh.shardCollection( "test.operations", { "operID" : "hashed" } )
{
  collectionsharded: 'test.operations',
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727860161, i: 31 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1727860161, i: 31 })
}
```

3. Т.к. таблица небольшая, то то уменьшаю размер chunk до 1Мб, чтобы запустилась балансировка:
```
[direct: mongos] admin> use config
switched to db config
db.settings.updateOne( { _id: "chunksize" }, { $set: { _id: "chunksize", value: 1 } }, { upsert: true } )
```

4. Через некоторое время проверяю, что таблица распределилась по шардам:
```
[direct: mongos] config> use test
switched to db test
[direct: mongos] test> db.operations.getShardDistribution()
Shard shard01 at shard01/lab4:27017,lab5:27017,lab6:27017
{
  data: '3MiB',
  docs: 28083,
  chunks: 3,
  'estimated data per chunk': '1MiB',
  'estimated docs per chunk': 9361
}
---
Shard shard02 at shard02/lab7:27017,lab8:27017,lab9:27017
{
  data: '3MiB',
  docs: 28083,
  chunks: 3,
  'estimated data per chunk': '1MiB',
  'estimated docs per chunk': 9361
}
---
Shard shard03 at shard03/lab10:27017,lab11:27017,lab12:27017
{
  data: '4.69MiB',
  docs: 43834,
  chunks: 1,
  'estimated data per chunk': '4.69MiB',
  'estimated docs per chunk': 43834
}
---
Totals
{
  data: '10.71MiB',
  docs: 100000,
  chunks: 7,
  'Shard shard01': [
    '28.08 % data',
    '28.08 % docs in cluster',
    '112B avg obj size on shard'
  ],
  'Shard shard02': [
    '28.08 % data',
    '28.08 % docs in cluster',
    '112B avg obj size on shard'
  ],
  'Shard shard03': [
    '43.83 % data',
    '43.83 % docs in cluster',
    '112B avg obj size on shard'
  ]
}
```

5. Загружаю в коллекцию ещё 100 документов (методом, описанным чуть выше).

6. Проверяю, что документы распределились по шардам:
```
[direct: mongos] test> db.operations.getShardDistribution()
Shard shard01 at shard01/lab4:27017,lab5:27017,lab6:27017
{
  data: '3.01MiB',
  docs: 28110,
  chunks: 3,
  'estimated data per chunk': '1MiB',
  'estimated docs per chunk': 9370
}
---
Shard shard02 at shard02/lab7:27017,lab8:27017,lab9:27017
{
  data: '3.01MiB',
  docs: 28107,
  chunks: 2,
  'estimated data per chunk': '1.5MiB',
  'estimated docs per chunk': 14053
}
---
Shard shard03 at shard03/lab10:27017,lab11:27017,lab12:27017
{
  data: '4.7MiB',
  docs: 43885,
  chunks: 1,
  'estimated data per chunk': '4.7MiB',
  'estimated docs per chunk': 43885
}
---
Totals
{
  data: '10.72MiB',
  docs: 100102,
  chunks: 6,
  'Shard shard01': [
    '28.08 % data',
    '28.08 % docs in cluster',
    '112B avg obj size on shard'
  ],
  'Shard shard02': [
    '28.08 % data',
    '28.07 % docs in cluster',
    '112B avg obj size on shard'
  ],
  'Shard shard03': [
    '43.83 % data',
    '43.84 % docs in cluster',
    '112B avg obj size on shard'
  ]
}
```

### Проверка отработки отказов кластером


