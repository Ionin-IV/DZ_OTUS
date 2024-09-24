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
  * сервер lab7
  * сервер lab8
  * сервер lab9
- 3-я replica set (мастер - реплика - арбитр):
  * сервер lab10
  * сервер lab11
  * сервер lab12
- 1 сервер роутер для работы с кластром:
  * сервер lab13

Примечание:
- во втором шарде сделаю сервера с прописанным приоритетом роли мастера
- в третьем шарде искользую арбитр вместо одной реплики, для того чтобы показать разницу в отработке отказа на разных конфигурациях

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

6. Запрашиваю статус replica set:
```
cfg_replica [direct: primary] config> rs.status()
{
  set: 'cfg_replica',
  date: ISODate('2024-09-24T13:42:56.188Z'),
  myState: 1,
  term: Long('1'),
  syncSourceHost: '',
  syncSourceId: -1,
  configsvr: true,
  heartbeatIntervalMillis: Long('2000'),
  majorityVoteCount: 2,
  writeMajorityCount: 2,
  votingMembersCount: 3,
  writableVotingMembersCount: 3,
  optimes: {
    lastCommittedOpTime: { ts: Timestamp({ t: 1727185375, i: 1 }), t: Long('1') },
    lastCommittedWallTime: ISODate('2024-09-24T13:42:55.363Z'),
    readConcernMajorityOpTime: { ts: Timestamp({ t: 1727185375, i: 1 }), t: Long('1') },
    appliedOpTime: { ts: Timestamp({ t: 1727185375, i: 1 }), t: Long('1') },
    durableOpTime: { ts: Timestamp({ t: 1727185375, i: 1 }), t: Long('1') },
    lastAppliedWallTime: ISODate('2024-09-24T13:42:55.363Z'),
    lastDurableWallTime: ISODate('2024-09-24T13:42:55.363Z')
  },
  lastStableRecoveryTimestamp: Timestamp({ t: 1727185358, i: 1 }),
  electionCandidateMetrics: {
    lastElectionReason: 'electionTimeout',
    lastElectionDate: ISODate('2024-09-24T13:41:48.846Z'),
    electionTerm: Long('1'),
    lastCommittedOpTimeAtElection: { ts: Timestamp({ t: 1727185298, i: 1 }), t: Long('-1') },
    lastSeenOpTimeAtElection: { ts: Timestamp({ t: 1727185298, i: 1 }), t: Long('-1') },
    numVotesNeeded: 2,
    priorityAtElection: 1,
    electionTimeoutMillis: Long('10000'),
    numCatchUpOps: Long('0'),
    newTermStartDate: ISODate('2024-09-24T13:41:48.913Z'),
    wMajorityWriteAvailabilityDate: ISODate('2024-09-24T13:41:49.433Z')
  },
  members: [
    {
      _id: 0,
      name: 'lab1:27019',
      health: 1,
      state: 1,
      stateStr: 'PRIMARY',
      uptime: 245,
      optime: { ts: Timestamp({ t: 1727185375, i: 1 }), t: Long('1') },
      optimeDate: ISODate('2024-09-24T13:42:55.000Z'),
      lastAppliedWallTime: ISODate('2024-09-24T13:42:55.363Z'),
      lastDurableWallTime: ISODate('2024-09-24T13:42:55.363Z'),
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: 'Could not find member to sync from',
      electionTime: Timestamp({ t: 1727185308, i: 1 }),
      electionDate: ISODate('2024-09-24T13:41:48.000Z'),
      configVersion: 1,
      configTerm: 1,
      self: true,
      lastHeartbeatMessage: ''
    },
    {
      _id: 1,
      name: 'lab2:27019',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 77,
      optime: { ts: Timestamp({ t: 1727185374, i: 1 }), t: Long('1') },
      optimeDurable: { ts: Timestamp({ t: 1727185374, i: 1 }), t: Long('1') },
      optimeDate: ISODate('2024-09-24T13:42:54.000Z'),
      optimeDurableDate: ISODate('2024-09-24T13:42:54.000Z'),
      lastAppliedWallTime: ISODate('2024-09-24T13:42:55.363Z'),
      lastDurableWallTime: ISODate('2024-09-24T13:42:55.363Z'),
      lastHeartbeat: ISODate('2024-09-24T13:42:55.224Z'),
      lastHeartbeatRecv: ISODate('2024-09-24T13:42:55.906Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'lab1:27019',
      syncSourceId: 0,
      infoMessage: '',
      configVersion: 1,
      configTerm: 1
    },
    {
      _id: 2,
      name: 'lab3:27019',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 77,
      optime: { ts: Timestamp({ t: 1727185374, i: 1 }), t: Long('1') },
      optimeDurable: { ts: Timestamp({ t: 1727185374, i: 1 }), t: Long('1') },
      optimeDate: ISODate('2024-09-24T13:42:54.000Z'),
      optimeDurableDate: ISODate('2024-09-24T13:42:54.000Z'),
      lastAppliedWallTime: ISODate('2024-09-24T13:42:55.363Z'),
      lastDurableWallTime: ISODate('2024-09-24T13:42:55.363Z'),
      lastHeartbeat: ISODate('2024-09-24T13:42:55.224Z'),
      lastHeartbeatRecv: ISODate('2024-09-24T13:42:55.904Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'lab1:27019',
      syncSourceId: 0,
      infoMessage: '',
      configVersion: 1,
      configTerm: 1
    }
  ],
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1727185375, i: 1 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1727185375, i: 1 })
}
```

### Создание 1-й replica set

