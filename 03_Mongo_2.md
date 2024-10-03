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
- 1 сервер балансировщика mongos:
  * сервер lab13

Примечание: во втором шарде сделаю сервера с прописанным приоритетом роли мастера.

### Установка ПО MongoDB

На каждом сервере устанавливаю ПО MongoDB по инструкции, описанной в предыдущем домашнем задании:
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

### Создание балансировщика mongos

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

3. Т.к. коллекция небольшая, то уменьшаю размер chunk до 1Мб, чтобы запустилась балансировка:
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
Shard shard03 at shard03/lab10:27017,lab11:27017,lab12:27017
{
  data: '4.7MiB',
  docs: 43883,
  chunks: 1,
  'estimated data per chunk': '4.7MiB',
  'estimated docs per chunk': 43883
}
---
Shard shard01 at shard01/lab4:27017,lab5:27017,lab6:27017
{
  data: '3.01MiB',
  docs: 28114,
  chunks: 2,
  'estimated data per chunk': '1.5MiB',
  'estimated docs per chunk': 14057
}
---
Shard shard02 at shard02/lab7:27017,lab8:27017,lab9:27017
{
  data: '3MiB',
  docs: 28103,
  chunks: 2,
  'estimated data per chunk': '1.5MiB',
  'estimated docs per chunk': 14051
}
---
Totals
{
  data: '10.72MiB',
  docs: 100100,
  chunks: 5,
  'Shard shard03': [
    '43.83 % data',
    '43.83 % docs in cluster',
    '112B avg obj size on shard'
  ],
  'Shard shard01': [
    '28.08 % data',
    '28.08 % docs in cluster',
    '112B avg obj size on shard'
  ],
  'Shard shard02': [
    '28.07 % data',
    '28.07 % docs in cluster',
    '112B avg obj size on shard'
  ]
}

```

### Проверка отработки отказов кластером

1. Останавливаю сервис mongod на 1-м узле 1-го шарда, кторый находится в роли primary. Primary становится 2-й узел:
```
shard01 [direct: primary] test> rs.status()
{
  set: 'shard01',
  date: ISODate('2024-10-02T12:31:46.199Z'),
  myState: 1,
  term: Long('9'),
  syncSourceHost: '',
  syncSourceId: -1,
  heartbeatIntervalMillis: Long('2000'),
  majorityVoteCount: 2,
  writeMajorityCount: 2,
  votingMembersCount: 3,
  writableVotingMembersCount: 3,
  optimes: {
    lastCommittedOpTime: { ts: Timestamp({ t: 1727872300, i: 1 }), t: Long('9') },
    lastCommittedWallTime: ISODate('2024-10-02T12:31:40.524Z'),
    readConcernMajorityOpTime: { ts: Timestamp({ t: 1727872300, i: 1 }), t: Long('9') },
    appliedOpTime: { ts: Timestamp({ t: 1727872300, i: 1 }), t: Long('9') },
    durableOpTime: { ts: Timestamp({ t: 1727872300, i: 1 }), t: Long('9') },
    lastAppliedWallTime: ISODate('2024-10-02T12:31:40.524Z'),
    lastDurableWallTime: ISODate('2024-10-02T12:31:40.524Z')
  },
  lastStableRecoveryTimestamp: Timestamp({ t: 1727872290, i: 1 }),
  electionCandidateMetrics: {
    lastElectionReason: 'stepUpRequestSkipDryRun',
    lastElectionDate: ISODate('2024-10-02T12:31:10.505Z'),
    electionTerm: Long('9'),
    lastCommittedOpTimeAtElection: { ts: Timestamp({ t: 1727872270, i: 1 }), t: Long('8') },
    lastSeenOpTimeAtElection: { ts: Timestamp({ t: 1727872270, i: 1 }), t: Long('8') },
    numVotesNeeded: 2,
    priorityAtElection: 1,
    electionTimeoutMillis: Long('10000'),
    priorPrimaryMemberId: 0,
    numCatchUpOps: Long('0'),
    newTermStartDate: ISODate('2024-10-02T12:31:10.513Z'),
    wMajorityWriteAvailabilityDate: ISODate('2024-10-02T12:31:10.521Z')
  },
  electionParticipantMetrics: {
    votedForCandidate: true,
    electionTerm: Long('8'),
    lastVoteDate: ISODate('2024-10-02T12:28:40.020Z'),
    electionCandidateMemberId: 0,
    voteReason: '',
    lastAppliedOpTimeAtElection: { ts: Timestamp({ t: 1727872103, i: 1 }), t: Long('7') },
    maxAppliedOpTimeInSet: { ts: Timestamp({ t: 1727872103, i: 1 }), t: Long('7') },
    priorityAtElection: 1
  },
  members: [
    {
      _id: 0,
      name: 'lab4:27017',
      health: 0,
      state: 8,
      stateStr: '(not reachable/healthy)',
      uptime: 0,
      optime: { ts: Timestamp({ t: 0, i: 0 }), t: Long('-1') },
      optimeDurable: { ts: Timestamp({ t: 0, i: 0 }), t: Long('-1') },
      optimeDate: ISODate('1970-01-01T00:00:00.000Z'),
      optimeDurableDate: ISODate('1970-01-01T00:00:00.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:31:20.521Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:31:20.521Z'),
      lastHeartbeat: ISODate('2024-10-02T12:31:44.932Z'),
      lastHeartbeatRecv: ISODate('2024-10-02T12:31:25.088Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: 'Error connecting to lab4:27017 (192.168.1.24:27017) :: caused by :: onInvoke :: caused by :: Connection refused',
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      configVersion: 1,
      configTerm: 9
    },
    {
      _id: 1,
      name: 'lab5:27017',
      health: 1,
      state: 1,
      stateStr: 'PRIMARY',
      uptime: 1510,
      optime: { ts: Timestamp({ t: 1727872300, i: 1 }), t: Long('9') },
      optimeDate: ISODate('2024-10-02T12:31:40.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:31:40.524Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:31:40.524Z'),
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      electionTime: Timestamp({ t: 1727872270, i: 2 }),
      electionDate: ISODate('2024-10-02T12:31:10.000Z'),
      configVersion: 1,
      configTerm: 9,
      self: true,
      lastHeartbeatMessage: ''
    },
    {
      _id: 2,
      name: 'lab6:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 83,
      optime: { ts: Timestamp({ t: 1727872300, i: 1 }), t: Long('9') },
      optimeDurable: { ts: Timestamp({ t: 1727872300, i: 1 }), t: Long('9') },
      optimeDate: ISODate('2024-10-02T12:31:40.000Z'),
      optimeDurableDate: ISODate('2024-10-02T12:31:40.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:31:40.524Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:31:40.524Z'),
      lastHeartbeat: ISODate('2024-10-02T12:31:44.805Z'),
      lastHeartbeatRecv: ISODate('2024-10-02T12:31:44.559Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'lab5:27017',
      syncSourceId: 1,
      infoMessage: '',
      configVersion: 1,
      configTerm: 9
    }
  ],
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727872301, i: 1 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1727872300, i: 1 })
}
```

2. Загружаю в БД 100 документов. Операция проходит успешно.
```
[root@lab13 ~]# mongoimport --db=test --collection=operations --file=3.json
2024-10-02T15:41:02.962+0300    connected to: mongodb://localhost/
2024-10-02T15:41:02.976+0300    100 document(s) imported successfully. 0 document(s) failed to import.
```

3. Проверяю, что данные распределились по шардам:
```
[direct: mongos] test> db.operations.getShardDistribution()
Shard shard01 at shard01/lab4:27017,lab5:27017,lab6:27017
{
  data: '3.01MiB',
  docs: 28138,
  chunks: 2,
  'estimated data per chunk': '1.5MiB',
  'estimated docs per chunk': 14069
}
---
Shard shard03 at shard03/lab10:27017,lab11:27017,lab12:27017
{
  data: '4.7MiB',
  docs: 43936,
  chunks: 1,
  'estimated data per chunk': '4.7MiB',
  'estimated docs per chunk': 43936
}
---
Shard shard02 at shard02/lab7:27017,lab8:27017,lab9:27017
{
  data: '3.01MiB',
  docs: 28126,
  chunks: 2,
  'estimated data per chunk': '1.5MiB',
  'estimated docs per chunk': 14063
}
---
Totals
{
  data: '10.73MiB',
  docs: 100200,
  chunks: 5,
  'Shard shard01': [
    '28.08 % data',
    '28.08 % docs in cluster',
    '112B avg obj size on shard'
  ],
  'Shard shard03': [
    '43.84 % data',
    '43.84 % docs in cluster',
    '112B avg obj size on shard'
  ],
  'Shard shard02': [
    '28.07 % data',
    '28.06 % docs in cluster',
    '112B avg obj size on shard'
  ]
}
```

4. Останавливаю сервис mongod на 2-м узле 1-го шарда, кторый находится в роли primary. Оставшийся 3-й узел остался в роли secondary:
```
shard01 [direct: secondary] test> rs.status()
{
  set: 'shard01',
  date: ISODate('2024-10-02T12:43:14.566Z'),
  myState: 2,
  term: Long('10'),
  syncSourceHost: '',
  syncSourceId: -1,
  heartbeatIntervalMillis: Long('2000'),
  majorityVoteCount: 2,
  writeMajorityCount: 2,
  votingMembersCount: 3,
  writableVotingMembersCount: 3,
  optimes: {
    lastCommittedOpTime: { ts: Timestamp({ t: 1727872970, i: 1 }), t: Long('9') },
    lastCommittedWallTime: ISODate('2024-10-02T12:42:50.833Z'),
    readConcernMajorityOpTime: { ts: Timestamp({ t: 1727872970, i: 1 }), t: Long('9') },
    appliedOpTime: { ts: Timestamp({ t: 1727872970, i: 1 }), t: Long('9') },
    durableOpTime: { ts: Timestamp({ t: 1727872970, i: 1 }), t: Long('9') },
    lastAppliedWallTime: ISODate('2024-10-02T12:42:50.833Z'),
    lastDurableWallTime: ISODate('2024-10-02T12:42:50.833Z')
  },
  lastStableRecoveryTimestamp: Timestamp({ t: 1727872932, i: 4 }),
  electionParticipantMetrics: {
    votedForCandidate: true,
    electionTerm: Long('9'),
    lastVoteDate: ISODate('2024-10-02T12:31:10.079Z'),
    electionCandidateMemberId: 1,
    voteReason: '',
    lastAppliedOpTimeAtElection: { ts: Timestamp({ t: 1727872270, i: 1 }), t: Long('8') },
    maxAppliedOpTimeInSet: { ts: Timestamp({ t: 1727872270, i: 1 }), t: Long('8') },
    priorityAtElection: 1
  },
  members: [
    {
      _id: 0,
      name: 'lab4:27017',
      health: 0,
      state: 8,
      stateStr: '(not reachable/healthy)',
      uptime: 0,
      optime: { ts: Timestamp({ t: 0, i: 0 }), t: Long('-1') },
      optimeDurable: { ts: Timestamp({ t: 0, i: 0 }), t: Long('-1') },
      optimeDate: ISODate('1970-01-01T00:00:00.000Z'),
      optimeDurableDate: ISODate('1970-01-01T00:00:00.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:31:10.073Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:31:10.073Z'),
      lastHeartbeat: ISODate('2024-10-02T12:43:14.151Z'),
      lastHeartbeatRecv: ISODate('2024-10-02T12:31:24.660Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: 'Error connecting to lab4:27017 (192.168.1.24:27017) :: caused by :: onInvoke :: caused by :: Connection refused',
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      configVersion: 1,
      configTerm: 9
    },
    {
      _id: 1,
      name: 'lab5:27017',
      health: 0,
      state: 8,
      stateStr: '(not reachable/healthy)',
      uptime: 0,
      optime: { ts: Timestamp({ t: 0, i: 0 }), t: Long('-1') },
      optimeDurable: { ts: Timestamp({ t: 0, i: 0 }), t: Long('-1') },
      optimeDate: ISODate('1970-01-01T00:00:00.000Z'),
      optimeDurableDate: ISODate('1970-01-01T00:00:00.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:42:50.833Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:42:50.833Z'),
      lastHeartbeat: ISODate('2024-10-02T12:43:14.235Z'),
      lastHeartbeatRecv: ISODate('2024-10-02T12:43:06.433Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: 'Error connecting to lab5:27017 (192.168.1.25:27017) :: caused by :: onInvoke :: caused by :: Connection refused',
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      configVersion: 1,
      configTerm: 9
    },
    {
      _id: 2,
      name: 'lab6:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 773,
      optime: { ts: Timestamp({ t: 1727872970, i: 1 }), t: Long('9') },
      optimeDate: ISODate('2024-10-02T12:42:50.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:42:50.833Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:42:50.833Z'),
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: 'Could not find member to sync from',
      configVersion: 1,
      configTerm: 9,
      self: true,
      lastHeartbeatMessage: ''
    }
  ],
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727872992, i: 1 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1727872970, i: 1 })
}
```

5. Команда просмотра распределения коллекции по шардам выдаёт ошибку:
```
[direct: mongos] test> db.operations.getShardDistribution()
MongoServerError[FailedToSatisfyReadPreference]: Could not find host matching read preference { mode: "primary" } for set shard01
```

6. При загрузке ещё 100 документов, 35 из них не загружается из-за недоступности 1-го шарда:
```
[root@lab13 ~]# mongoimport --db=test --collection=operations --file=4.json
2024-10-02T15:48:38.754+0300    connected to: mongodb://localhost/
2024-10-02T15:48:41.754+0300    [########################] test.operations      14.0KB/14.0KB (100.0%)
2024-10-02T15:48:44.755+0300    [########################] test.operations      14.0KB/14.0KB (100.0%)
2024-10-02T15:48:47.755+0300    [########################] test.operations      14.0KB/14.0KB (100.0%)
2024-10-02T15:48:50.755+0300    [########################] test.operations      14.0KB/14.0KB (100.0%)
2024-10-02T15:48:53.755+0300    [########################] test.operations      14.0KB/14.0KB (100.0%)
2024-10-02T15:48:53.756+0300    [########################] test.operations      14.0KB/14.0KB (100.0%)
2024-10-02T15:48:53.756+0300    Failed: bulk write exception: write errors: [Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, Write results unavailable from failing to target a host in the shard shard01 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard01, +23 more errors...]
2024-10-02T15:48:53.756+0300    65 document(s) imported successfully. 35 document(s) failed to import.
```

7. Запускаю остановленные ранее сервисы mongod на 1-2 узлах. 3-й узел становится primary, а остальные secondary:
```
shard01 [direct: primary] test> rs.status()
{
  set: 'shard01',
  date: ISODate('2024-10-02T12:50:32.007Z'),
  myState: 1,
  term: Long('11'),
  syncSourceHost: '',
  syncSourceId: -1,
  heartbeatIntervalMillis: Long('2000'),
  majorityVoteCount: 2,
  writeMajorityCount: 2,
  votingMembersCount: 3,
  writableVotingMembersCount: 3,
  optimes: {
    lastCommittedOpTime: { ts: Timestamp({ t: 1727873422, i: 2 }), t: Long('11') },
    lastCommittedWallTime: ISODate('2024-10-02T12:50:22.517Z'),
    readConcernMajorityOpTime: { ts: Timestamp({ t: 1727873422, i: 2 }), t: Long('11') },
    appliedOpTime: { ts: Timestamp({ t: 1727873422, i: 2 }), t: Long('11') },
    durableOpTime: { ts: Timestamp({ t: 1727873422, i: 2 }), t: Long('11') },
    lastAppliedWallTime: ISODate('2024-10-02T12:50:22.517Z'),
    lastDurableWallTime: ISODate('2024-10-02T12:50:22.517Z')
  },
  lastStableRecoveryTimestamp: Timestamp({ t: 1727872970, i: 1 }),
  electionCandidateMetrics: {
    lastElectionReason: 'electionTimeout',
    lastElectionDate: ISODate('2024-10-02T12:50:22.505Z'),
    electionTerm: Long('11'),
    lastCommittedOpTimeAtElection: { ts: Timestamp({ t: 1727872970, i: 1 }), t: Long('9') },
    lastSeenOpTimeAtElection: { ts: Timestamp({ t: 1727872970, i: 1 }), t: Long('9') },
    numVotesNeeded: 2,
    priorityAtElection: 1,
    electionTimeoutMillis: Long('10000'),
    numCatchUpOps: Long('0'),
    newTermStartDate: ISODate('2024-10-02T12:50:22.517Z'),
    wMajorityWriteAvailabilityDate: ISODate('2024-10-02T12:50:22.532Z')
  },
  electionParticipantMetrics: {
    votedForCandidate: true,
    electionTerm: Long('9'),
    lastVoteDate: ISODate('2024-10-02T12:31:10.079Z'),
    electionCandidateMemberId: 1,
    voteReason: '',
    lastAppliedOpTimeAtElection: { ts: Timestamp({ t: 1727872270, i: 1 }), t: Long('8') },
    maxAppliedOpTimeInSet: { ts: Timestamp({ t: 1727872270, i: 1 }), t: Long('8') },
    priorityAtElection: 1
  },
  members: [
    {
      _id: 0,
      name: 'lab4:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 16,
      optime: { ts: Timestamp({ t: 1727873422, i: 2 }), t: Long('11') },
      optimeDurable: { ts: Timestamp({ t: 1727873422, i: 2 }), t: Long('11') },
      optimeDate: ISODate('2024-10-02T12:50:22.000Z'),
      optimeDurableDate: ISODate('2024-10-02T12:50:22.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:50:22.517Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:50:22.517Z'),
      lastHeartbeat: ISODate('2024-10-02T12:50:30.525Z'),
      lastHeartbeatRecv: ISODate('2024-10-02T12:50:31.037Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'lab6:27017',
      syncSourceId: 2,
      infoMessage: '',
      configVersion: 1,
      configTerm: 11
    },
    {
      _id: 1,
      name: 'lab5:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 9,
      optime: { ts: Timestamp({ t: 1727873422, i: 2 }), t: Long('11') },
      optimeDurable: { ts: Timestamp({ t: 1727873422, i: 2 }), t: Long('11') },
      optimeDate: ISODate('2024-10-02T12:50:22.000Z'),
      optimeDurableDate: ISODate('2024-10-02T12:50:22.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:50:22.517Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:50:22.517Z'),
      lastHeartbeat: ISODate('2024-10-02T12:50:30.558Z'),
      lastHeartbeatRecv: ISODate('2024-10-02T12:50:29.593Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'lab6:27017',
      syncSourceId: 2,
      infoMessage: '',
      configVersion: 1,
      configTerm: 11
    },
    {
      _id: 2,
      name: 'lab6:27017',
      health: 1,
      state: 1,
      stateStr: 'PRIMARY',
      uptime: 1211,
      optime: { ts: Timestamp({ t: 1727873422, i: 2 }), t: Long('11') },
      optimeDate: ISODate('2024-10-02T12:50:22.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:50:22.517Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:50:22.517Z'),
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: 'Could not find member to sync from',
      electionTime: Timestamp({ t: 1727873422, i: 1 }),
      electionDate: ISODate('2024-10-02T12:50:22.000Z'),
      configVersion: 1,
      configTerm: 11,
      self: true,
      lastHeartbeatMessage: ''
    }
  ],
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727873429, i: 1 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1727873422, i: 2 })
}
```

8. Количество документов на 1-м шарде не изменилось, т.к. они не смогли загрузиться, а на 2-3 шардах докуменыт добавились:
```
[direct: mongos] test> db.operations.getShardDistribution()
Shard shard03 at shard03/lab10:27017,lab11:27017,lab12:27017
{
  data: '4.7MiB',
  docs: 43968,
  chunks: 1,
  'estimated data per chunk': '4.7MiB',
  'estimated docs per chunk': 43968
}
---
Shard shard01 at shard01/lab4:27017,lab5:27017,lab6:27017
{
  data: '3.01MiB',
  docs: 28138,
  chunks: 2,
  'estimated data per chunk': '1.5MiB',
  'estimated docs per chunk': 14069
}
---
Shard shard02 at shard02/lab7:27017,lab8:27017,lab9:27017
{
  data: '3.01MiB',
  docs: 28159,
  chunks: 2,
  'estimated data per chunk': '1.5MiB',
  'estimated docs per chunk': 14079
}
---
Totals
{
  data: '10.74MiB',
  docs: 100265,
  chunks: 5,
  'Shard shard03': [
    '43.84 % data',
    '43.85 % docs in cluster',
    '112B avg obj size on shard'
  ],
  'Shard shard01': [
    '28.06 % data',
    '28.06 % docs in cluster',
    '112B avg obj size on shard'
  ],
  'Shard shard02': [
    '28.08 % data',
    '28.08 % docs in cluster',
    '112B avg obj size on shard'
  ]
}
```

**ВЫВОД: для отказоусточивости, в каждой replica set должно быть не менее 3-х узлов.**

9. Останавливаю сервис mongod на 1-м узле 2-го шарда, кторый находится в роли primary. Primary становится 2-й узел:
```
shard02 [direct: primary] test> rs.status()
{
  set: 'shard02',
  date: ISODate('2024-10-02T12:52:52.047Z'),
  myState: 1,
  term: Long('6'),
  syncSourceHost: '',
  syncSourceId: -1,
  heartbeatIntervalMillis: Long('2000'),
  majorityVoteCount: 2,
  writeMajorityCount: 2,
  votingMembersCount: 3,
  writableVotingMembersCount: 3,
  optimes: {
    lastCommittedOpTime: { ts: Timestamp({ t: 1727873568, i: 1 }), t: Long('6') },
    lastCommittedWallTime: ISODate('2024-10-02T12:52:48.946Z'),
    readConcernMajorityOpTime: { ts: Timestamp({ t: 1727873568, i: 1 }), t: Long('6') },
    appliedOpTime: { ts: Timestamp({ t: 1727873568, i: 1 }), t: Long('6') },
    durableOpTime: { ts: Timestamp({ t: 1727873568, i: 1 }), t: Long('6') },
    lastAppliedWallTime: ISODate('2024-10-02T12:52:48.946Z'),
    lastDurableWallTime: ISODate('2024-10-02T12:52:48.946Z')
  },
  lastStableRecoveryTimestamp: Timestamp({ t: 1727873520, i: 1 }),
  electionCandidateMetrics: {
    lastElectionReason: 'stepUpRequestSkipDryRun',
    lastElectionDate: ISODate('2024-10-02T12:52:18.925Z'),
    electionTerm: Long('6'),
    lastCommittedOpTimeAtElection: { ts: Timestamp({ t: 1727873530, i: 1 }), t: Long('5') },
    lastSeenOpTimeAtElection: { ts: Timestamp({ t: 1727873530, i: 1 }), t: Long('5') },
    numVotesNeeded: 2,
    priorityAtElection: 90,
    electionTimeoutMillis: Long('10000'),
    priorPrimaryMemberId: 0,
    numCatchUpOps: Long('0'),
    newTermStartDate: ISODate('2024-10-02T12:52:18.936Z'),
    wMajorityWriteAvailabilityDate: ISODate('2024-10-02T12:52:18.942Z')
  },
  electionParticipantMetrics: {
    votedForCandidate: true,
    electionTerm: Long('5'),
    lastVoteDate: ISODate('2024-10-02T12:12:39.828Z'),
    electionCandidateMemberId: 0,
    voteReason: '',
    lastAppliedOpTimeAtElection: { ts: Timestamp({ t: 1727871155, i: 1 }), t: Long('4') },
    maxAppliedOpTimeInSet: { ts: Timestamp({ t: 1727871155, i: 1 }), t: Long('4') },
    priorityAtElection: 90
  },
  members: [
    {
      _id: 0,
      name: 'lab7:27017',
      health: 0,
      state: 8,
      stateStr: '(not reachable/healthy)',
      uptime: 0,
      optime: { ts: Timestamp({ t: 0, i: 0 }), t: Long('-1') },
      optimeDurable: { ts: Timestamp({ t: 0, i: 0 }), t: Long('-1') },
      optimeDate: ISODate('1970-01-01T00:00:00.000Z'),
      optimeDurableDate: ISODate('1970-01-01T00:00:00.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:52:23.327Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:52:23.327Z'),
      lastHeartbeat: ISODate('2024-10-02T12:52:50.960Z'),
      lastHeartbeatRecv: ISODate('2024-10-02T12:52:32.943Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: 'Error connecting to lab7:27017 (192.168.1.27:27017) :: caused by :: onInvoke :: caused by :: Connection refused',
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      configVersion: 2,
      configTerm: 6
    },
    {
      _id: 1,
      name: 'lab8:27017',
      health: 1,
      state: 1,
      stateStr: 'PRIMARY',
      uptime: 18949,
      optime: { ts: Timestamp({ t: 1727873568, i: 1 }), t: Long('6') },
      optimeDate: ISODate('2024-10-02T12:52:48.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:52:48.946Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:52:48.946Z'),
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      electionTime: Timestamp({ t: 1727873538, i: 2 }),
      electionDate: ISODate('2024-10-02T12:52:18.000Z'),
      configVersion: 2,
      configTerm: 6,
      self: true,
      lastHeartbeatMessage: ''
    },
    {
      _id: 2,
      name: 'lab9:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 18912,
      optime: { ts: Timestamp({ t: 1727873568, i: 1 }), t: Long('6') },
      optimeDurable: { ts: Timestamp({ t: 1727873568, i: 1 }), t: Long('6') },
      optimeDate: ISODate('2024-10-02T12:52:48.000Z'),
      optimeDurableDate: ISODate('2024-10-02T12:52:48.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:52:48.946Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:52:48.946Z'),
      lastHeartbeat: ISODate('2024-10-02T12:52:50.958Z'),
      lastHeartbeatRecv: ISODate('2024-10-02T12:52:50.955Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'lab8:27017',
      syncSourceId: 1,
      infoMessage: '',
      configVersion: 2,
      configTerm: 6
    }
  ],
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727873569, i: 1 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1727873568, i: 1 })
}
```

10. Запускаю сервис mongod на 1-м узле 2-го шарда. Он, в соответствии с заданными приоритетами, опять становится primary:
```
shard02 [direct: primary] test> rs.status()
{
  set: 'shard02',
  date: ISODate('2024-10-02T12:53:36.293Z'),
  myState: 1,
  term: Long('7'),
  syncSourceHost: '',
  syncSourceId: -1,
  heartbeatIntervalMillis: Long('2000'),
  majorityVoteCount: 2,
  writeMajorityCount: 2,
  votingMembersCount: 3,
  writableVotingMembersCount: 3,
  optimes: {
    lastCommittedOpTime: { ts: Timestamp({ t: 1727873613, i: 2 }), t: Long('7') },
    lastCommittedWallTime: ISODate('2024-10-02T12:53:33.190Z'),
    readConcernMajorityOpTime: { ts: Timestamp({ t: 1727873613, i: 2 }), t: Long('7') },
    appliedOpTime: { ts: Timestamp({ t: 1727873613, i: 2 }), t: Long('7') },
    durableOpTime: { ts: Timestamp({ t: 1727873613, i: 2 }), t: Long('7') },
    lastAppliedWallTime: ISODate('2024-10-02T12:53:33.190Z'),
    lastDurableWallTime: ISODate('2024-10-02T12:53:33.190Z')
  },
  lastStableRecoveryTimestamp: Timestamp({ t: 1727873543, i: 2 }),
  electionCandidateMetrics: {
    lastElectionReason: 'priorityTakeover',
    lastElectionDate: ISODate('2024-10-02T12:53:33.180Z'),
    electionTerm: Long('7'),
    lastCommittedOpTimeAtElection: { ts: Timestamp({ t: 1727873608, i: 1 }), t: Long('6') },
    lastSeenOpTimeAtElection: { ts: Timestamp({ t: 1727873608, i: 1 }), t: Long('6') },
    numVotesNeeded: 2,
    priorityAtElection: 100,
    electionTimeoutMillis: Long('10000'),
    priorPrimaryMemberId: 1,
    numCatchUpOps: Long('0'),
    newTermStartDate: ISODate('2024-10-02T12:53:33.190Z'),
    wMajorityWriteAvailabilityDate: ISODate('2024-10-02T12:53:33.205Z')
  },
  members: [
    {
      _id: 0,
      name: 'lab7:27017',
      health: 1,
      state: 1,
      stateStr: 'PRIMARY',
      uptime: 14,
      optime: { ts: Timestamp({ t: 1727873613, i: 2 }), t: Long('7') },
      optimeDate: ISODate('2024-10-02T12:53:33.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:53:33.190Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:53:33.190Z'),
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      electionTime: Timestamp({ t: 1727873613, i: 1 }),
      electionDate: ISODate('2024-10-02T12:53:33.000Z'),
      configVersion: 2,
      configTerm: 7,
      self: true,
      lastHeartbeatMessage: ''
    },
    {
      _id: 1,
      name: 'lab8:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 13,
      optime: { ts: Timestamp({ t: 1727873613, i: 2 }), t: Long('7') },
      optimeDurable: { ts: Timestamp({ t: 1727873613, i: 2 }), t: Long('7') },
      optimeDate: ISODate('2024-10-02T12:53:33.000Z'),
      optimeDurableDate: ISODate('2024-10-02T12:53:33.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:53:33.190Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:53:33.190Z'),
      lastHeartbeat: ISODate('2024-10-02T12:53:35.199Z'),
      lastHeartbeatRecv: ISODate('2024-10-02T12:53:35.693Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'lab7:27017',
      syncSourceId: 0,
      infoMessage: '',
      configVersion: 2,
      configTerm: 7
    },
    {
      _id: 2,
      name: 'lab9:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 13,
      optime: { ts: Timestamp({ t: 1727873613, i: 2 }), t: Long('7') },
      optimeDurable: { ts: Timestamp({ t: 1727873613, i: 2 }), t: Long('7') },
      optimeDate: ISODate('2024-10-02T12:53:33.000Z'),
      optimeDurableDate: ISODate('2024-10-02T12:53:33.000Z'),
      lastAppliedWallTime: ISODate('2024-10-02T12:53:33.190Z'),
      lastDurableWallTime: ISODate('2024-10-02T12:53:33.190Z'),
      lastHeartbeat: ISODate('2024-10-02T12:53:35.199Z'),
      lastHeartbeatRecv: ISODate('2024-10-02T12:53:35.198Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'lab8:27017',
      syncSourceId: 1,
      infoMessage: '',
      configVersion: 2,
      configTerm: 7
    }
  ],
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727873613, i: 2 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1727873613, i: 2 })
}
```

**ВЫВОД: если нужна жёсткая привязка роли к узлам, то это можно сделать с помощью приоритетов.**

### Включение авторизации

1. На одном из серверов генерирую ключ:
```
openssl rand -base64 756 > /etc/mongo_auth.key
```

2. Копирую ключ на остальные сервера.

3. Редактирую права на ключ:
```
chown mongod: /etc/mongo_auth.key
chmod 400 /etc/mongo_auth.key
```

4. Отключаю балансировку:
```
[direct: mongos] test> sh.stopBalancer()
{
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727943628, i: 4 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1727943628, i: 4 })
}
```

5. Останавливаю сервисы mongod/s на всех серверах.

6. Добавляю в конфигурационные фалы параметры:
```
security:
  keyFile: /etc/mongo_auth.key
```

7. Запускаю сервисы mongo на всех серверах.

8. Создаю администратора пользователей:
```
[direct: mongos] test> use admin
switched to db admin
[direct: mongos] admin> db.createUser(
...   {
...     user: "user_admin",
...     pwd:  passwordPrompt(),
...     roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
...   }
... )
Enter password
*********{
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727945108, i: 4 }),
    signature: {
      hash: Binary.createFromBase64('6qH2qZ61xasWQzCvXfNp2sMR4uE=', 0),
      keyId: Long('7420780864088309782')
    }
  },
  operationTime: Timestamp({ t: 1727945108, i: 4 })
}
```

9. Подключаюсь под созданным администратором пользователей:
```
[root@lab13 ~]# mongosh -u user_admin -p
Enter password: *********
Current Mongosh Log ID: 66fe59e229e43202aa964032
Connecting to:          mongodb://<credentials>@127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.1
Using MongoDB:          7.0.14
Using Mongosh:          2.3.1
```

10. Создаю администратора кластера:
```
[direct: mongos] test> use admin
switched to db admin
[direct: mongos] admin> db.createUser(
...   {
...     "user" : "cluster_admin",
...     "pwd" : passwordPrompt(),
...     roles: [ { "role" : "clusterAdmin", "db" : "admin" } ]
...   }
... )
Enter password
*********{
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727945296, i: 1 }),
    signature: {
      hash: Binary.createFromBase64('LkOwD4F4JlqFrwfGZlr1aHadwQY=', 0),
      keyId: Long('7420780864088309782')
    }
  },
  operationTime: Timestamp({ t: 1727945296, i: 1 })
}
```

11. Подключаюсь под администраторм кластера:
```
[root@lab13 ~]# mongosh -u cluster_admin -p
Enter password: *********
Current Mongosh Log ID: 66fe5a9f9378a97bf8964032
Connecting to:          mongodb://<credentials>@127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.1
Using MongoDB:          7.0.14
Using Mongosh:          2.3.1
```

12. Включаю выключенную ранее балансировку:
```
[direct: mongos] test> sh.startBalancer()
{
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727945440, i: 4 }),
    signature: {
      hash: Binary.createFromBase64('mriIqpKNcUFYKYiyFLy/bRlCM3I=', 0),
      keyId: Long('7420780864088309782')
    }
  },
  operationTime: Timestamp({ t: 1727945440, i: 4 })
}
```

### Создание пользователей

1. Подключаюсь под администратором пользователей:
```
[root@lab13 ~]# mongosh -u user_admin -p
Enter password: *********
Current Mongosh Log ID: 66fe66a63650649609964032
Connecting to:          mongodb://<credentials>@127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.1
Using MongoDB:          7.0.14
Using Mongosh:          2.3.1
```

2. Создаю пользователя test_rw с правами чтения/записи в БД test:
```
[direct: mongos] test> db.createUser(
...   {
...     user: "test_rw",
...     pwd:  passwordPrompt(),
...     roles: [ { role: "readWrite", db: "test" } ]
...   }
... )
Enter password
*******{
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727946868, i: 2 }),
    signature: {
      hash: Binary.createFromBase64('u407XKZ7Tnbu5kUx3sadBpLkp/k=', 0),
      keyId: Long('7420780864088309782')
    }
  },
  operationTime: Timestamp({ t: 1727946868, i: 2 })
}
```

3. Создаю пользователя test_ro с правами только чтения в БД test:
```
[direct: mongos] test> db.createUser(
...   {
...     user: "test_ro",
...     pwd:  passwordPrompt(),
...     roles: [ { role: "read", db: "test" } ]
...   }
... )
Enter password
*******{
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727946898, i: 1 }),
    signature: {
      hash: Binary.createFromBase64('DCs0Ddey8QphctlFafBW0feD7vo=', 0),
      keyId: Long('7420780864088309782')
    }
  },
  operationTime: Timestamp({ t: 1727946898, i: 1 })
}
```

### Тестирование прав созданных пользователей

1. Подключаюсь под пользователем test_rw:
```
[root@lab13 ~]# mongosh -u test_rw -p --authenticationDatabase test
Enter password: *******
Current Mongosh Log ID: 66fe6142f06b279438964032
Connecting to:          mongodb://<credentials>@127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=test&appName=mongosh+2.3.1
Using MongoDB:          7.0.14
Using Mongosh:          2.3.1
```

2. Успешно вношу документ в коллекцию:
```
[direct: mongos] test> db.operations.insertOne( { operID: 100300, date: "2024-10-01 02:00:00", name: "Иван Иванов", operations: -1200 } )
{
  acknowledged: true,
  insertedId: ObjectId('66fe61f4f06b279438964033')
}
```

3. Подключаюсь под пользователем test_ro:
```
[root@lab13 ~]# mongosh -u test_ro -p --authenticationDatabase test
Enter password: *******
Current Mongosh Log ID: 66fe6214be32da06ef964032
Connecting to:          mongodb://<credentials>@127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=test&appName=mongosh+2.3.1
Using MongoDB:          7.0.14
Using Mongosh:          2.3.1
```

4. При попытке добавления документа, получаю ошибку нехватки прав:
```
[direct: mongos] test> db.operations.insertOne( { operID: 100301, date: "2024-10-01 02:10:00", name: "Пётр Петров", operations: 3700 } )
MongoServerError[Unauthorized]: not authorized on test to execute command { insert: "operations", documents: [ { operID: 100301, date: "2024-10-01 02:10:00", name: "Пётр Петров", operations: 3700, _id: ObjectId('66fe625cbe32da06ef964033') } ], ordered: true, lsid: { id: UUID("9dedf46b-c617-4015-aaf0-778c040b3582") }, txnNumber: 1, $clusterTime: { clusterTime: Timestamp(1727947283, 1), signature: { hash: BinData(0, 2B1E7832C444BCD2E1412B58559857B1AEA759BF), keyId: 7420780864088309782 } }, $db: "test" }
```
