# Домашнее задание по лекции "Базовые возможности MongoDB"

## Задание

Необходимо:
- установить MongoDB одним из способов: ВМ, докер;
- заполнить данными;
- написать несколько запросов на выборку и обновление данных

Задание повышенной сложности*:
- создать индексы и сравнить производительность.

## Выполнение задания:

### Установка MongoDB:

1. Создаю ВМ в конфигурации: 2 ядра процессора, 2 Гб памяти, 15 Гб жесткий диск, ОС CentOS 7.9

2. Устанавливаю параметр минимального использования swap:
   * Добавляю в файл /etc/sysctl.conf строку:
      ```
      vm.swappiness = 1
      ```
   * Применяю параметр командой:
     ```
     sysctl -p
     ```

3. Отключаю Transparent Hugepages:
   * Создаю для сервиса файл /etc/systemd/system/disable-transparent-huge-pages.service со следующим содержимым:
      ```
      [Unit]
      Description=Disable Transparent Hugepages (THP)
      DefaultDependencies=no
      After=sysinit.target local-fs.target
      Before=mongod.service
      [Service]
      Type=oneshot
      ExecStart=/bin/sh -c 'echo never | tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null && echo never | tee /sys/kernel/mm/transparent_hugepage/defrag > /dev/null'
      [Install]
      WantedBy=basic.target
      ```
   * Перечитываю список сервисов командой:
     ```
     systemctl daemon-reload
     ```
   * Включаю автозапуск и заупускаю сервис disable-transparent-huge-pages командами:
     ```
     systemctl enable disable-transparent-huge-pages
     systemctl start disable-transparent-huge-pages
     ```

4. Отключаю SELINUX:
   * В файле /etc/selinux/config ставлю параметр:
     ```
     SELINUX=disabled
     ```
   * Перезагружаю сервер, для применения параметра.

5. Для репозитория MongoDB создаю файл /etc/yum.repos.d/mongodb-org-7.0.repo для репозитория MongoDB со следующим содержимым:
   ```
   [mongodb-org-7.0]
   name=MongoDB Repository
   baseurl=https://repo.mongodb.org/yum/redhat/7/mongodb-org/7.0/x86_64/
   gpgcheck=1
   enabled=1
   gpgkey=https://pgp.mongodb.com/server-7.0.asc
   ```

6. Устанавливаю MongoDB командой:
   ```
   yum install mongodb-org
   ```

7. Меняю директорию для данных БД:
   * Создаю директорию /data/mongodb и даю на неё необходимые права командами:
     ```
     mkdir -p /data/mongodb
     chown -R mongod:mongod /data/mongodb
     ```
   * Меняю параметр расположения данных БД в файле параметров /etc/mongod.conf:
     ```
     storage:
       dbPath: /data/mongodb
     ```

10. Включаю автозапуск и запускаю сервис MongoDB:
    ```
    systemctl enable mongod
    systemctl start mongod
    ```

### Заполнение БД данными

Создаю коллекцию operations прихода/расхода денежных средств со следующими полями:
* date - дата операции
* name - имя и фамилия
* operation - приход/расход денежных средств (положительное число - приход, отрицательное - расход)

Для этого выполняю следующие действия:
1. Создаю нижеследующий скрипт (bash linux), генерирующий данные в json-файл для загрузки в БД:
   ```
   #!/bin/sh

   NAMES=("Иван Иванов" "Пётр Петров" "Сидор Сидоров")  # массив с именами и фамилиями

   for (( i=1; i <= 10000; i++ ))  # цикл с 10000 повторений
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

### Работа с данными в БД

1. Проверяю количество документов в загруженной коллекции:
   ```
   test> db.operations.countDocuments()
   10000
   ```
   
2. Запрашиваю количество документов по операциям Ивана Иванова:
   ```
   test> db.operations.countDocuments({name: "Иван Иванов"})
   3260
   ```

3. Запрашиваю данные по Петру Петрову, отсортированные по возрастанию даты и ограниченные выводом  пяти документов:
   ```
   test> db.operations.find({name: "Пётр Петров"}).limit(5).sort({date: 1})
   [
     {
       _id: ObjectId('66eaa048c8154ce245bd6b0b'),
       date: '2024-09-11 13:47:00',
       name: 'Пётр Петров',
       operation: 5848
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6b07'),
       date: '2024-09-11 13:50:00',
       name: 'Пётр Петров',
       operation: 9629
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6b01'),
       date: '2024-09-11 13:56:00',
       name: 'Пётр Петров',
       operation: -1755
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6b00'),
       date: '2024-09-11 13:57:00',
       name: 'Пётр Петров',
       operation: 5889
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6afd'),
       date: '2024-09-11 14:01:00',
       name: 'Пётр Петров',
       operation: 4561
     }
   ]
   ```

4. Запрашиваю минимальные и максимальные значения дат операций по именам/фамилиям:
   ```
   test> db.operations.aggregate([{ $group: { _id: "$name", minDate: {$min: "$date"},  maxDate: {$max: "$date"}}}])
   [
     {
       _id: 'Пётр Петров',
       minDate: '2024-09-11 13:47:00',
       maxDate: '2024-09-18 12:20:00'
     },
     {
       _id: 'Иван Иванов',
       minDate: '2024-09-11 13:48:00',
       maxDate: '2024-09-18 12:16:00'
     },
     {
       _id: 'Сидор Сидоров',
       minDate: '2024-09-11 13:49:00',
       maxDate: '2024-09-18 12:19:00'
     }
   ]
   ```

5. Запрашиваю ограниченные по времени данные приходов по Сидору Сидорову:
   ```
   test> db.operations.find( { $and: [ { name: "Сидор Сидоров"}, { date: { $gte: "2024-09-11 14:00:00" } }, { date: { $lt: "2024-09-11 14:30:00" }}, { operation: { $gt: 0 } } ]  } )
   [
     {
       _id: ObjectId('66eaa048c8154ce245bd6ae8'),
       date: '2024-09-11 14:21:00',
       name: 'Сидор Сидоров',
       operation: 1199
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6aed'),
       date: '2024-09-11 14:16:00',
       name: 'Сидор Сидоров',
       operation: 9696
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6aee'),
       date: '2024-09-11 14:15:00',
       name: 'Сидор Сидоров',
       operation: 2997
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6af5'),
       date: '2024-09-11 14:08:00',
       name: 'Сидор Сидоров',
       operation: 7634
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6af7'),
       date: '2024-09-11 14:06:00',
       name: 'Сидор Сидоров',
       operation: 7896
     }
   ]
   ```

6. Уменшаю на 1000 приходы по Сидору Сидорову в запрошенном ранее периоде времени:
   ```
   test> db.operations.updateMany( { $and: [ { name: "Сидор Сидоров"}, { date: { $gte: "2024-09-11 14:00:00" } }, { date: { $lt: "2024-09-11 14:30:000" }}, { operation: { $gt: 0 } } ]  }, { $inc: { operation: -1000 } } )
   {
     acknowledged: true,
     insertedId: null,
     matchedCount: 5,
     modifiedCount: 5,
     upsertedCount: 0
   }
   ```

7. Проверяю результат предыдущей команды:
   ```
   test> db.operations.find( { $and: [ { name: "Сидор Сидоров"}, { date: { $gte: "2024-09-11 14:00:00" } }, { date: { $lt: "2024-09-11 14:30:00" }}, { operation: { $gt: 0 } } ]  } )
   [
     {
       _id: ObjectId('66eaa048c8154ce245bd6ae8'),
       date: '2024-09-11 14:21:00',
       name: 'Сидор Сидоров',
       operation: 199
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6aed'),
       date: '2024-09-11 14:16:00',
       name: 'Сидор Сидоров',
       operation: 8696
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6aee'),
       date: '2024-09-11 14:15:00',
       name: 'Сидор Сидоров',
       operation: 1997
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6af5'),
       date: '2024-09-11 14:08:00',
       name: 'Сидор Сидоров',
       operation: 6634
     },
     {
       _id: ObjectId('66eaa048c8154ce245bd6af7'),
       date: '2024-09-11 14:06:00',
       name: 'Сидор Сидоров',
       operation: 6896
     }
   ]
   ```

### Создание индексов и сравнение производительности

1. Получаю статистику выполнения запроса до создания индекса:
   ```
   test> db.operations.find( { $and: [ { name: "Сидор Сидоров"}, { date: { $gte: "2024-09-11 14:00:00" } }, { date: { $lt: "2024-09-12 14:00:00" }} ]  } ).explain("executionStats")
   {
     explainVersion: '1',
     queryPlanner: {
       namespace: 'test.operations',
       indexFilterSet: false,
       parsedQuery: {
         '$and': [
           { name: { '$eq': 'Сидор Сидоров' } },
           { date: { '$lt': '2024-09-12 14:00:00' } },
           { date: { '$gte': '2024-09-11 14:00:00' } }
         ]
       },
       queryHash: '21D08A2C',
       planCacheKey: '21D08A2C',
       maxIndexedOrSolutionsReached: false,
       maxIndexedAndSolutionsReached: false,
       maxScansToExplodeReached: false,
       winningPlan: {
         stage: 'COLLSCAN',
         filter: {
           '$and': [
             { name: { '$eq': 'Сидор Сидоров' } },
             { date: { '$lt': '2024-09-12 14:00:00' } },
             { date: { '$gte': '2024-09-11 14:00:00' } }
           ]
         },
         direction: 'forward'
       },
       rejectedPlans: []
     },
     executionStats: {
       executionSuccess: true,
       nReturned: 506,
       executionTimeMillis: 5,
       totalKeysExamined: 0,
       totalDocsExamined: 10000,
       executionStages: {
         stage: 'COLLSCAN',
         filter: {
           '$and': [
             { name: { '$eq': 'Сидор Сидоров' } },
             { date: { '$lt': '2024-09-12 14:00:00' } },
             { date: { '$gte': '2024-09-11 14:00:00' } }
           ]
         },
         nReturned: 506,
         executionTimeMillisEstimate: 0,
         works: 10001,
         advanced: 506,
         needTime: 9494,
         needYield: 0,
         saveState: 10,
         restoreState: 10,
         isEOF: 1,
         direction: 'forward',
         docsExamined: 10000
       }
     },
     command: {
       find: 'operations',
       filter: {
         '$and': [
           { name: 'Сидор Сидоров' },
           { date: { '$gte': '2024-09-11 14:00:00' } },
           { date: { '$lt': '2024-09-12 14:00:00' } }
         ]
       },
       '$db': 'test'
     },
     serverInfo: {
       host: 'lab1',
       port: 27017,
       version: '7.0.14',
       gitVersion: 'ce59cfc6a3c5e5c067dca0d30697edd68d4f5188'
     },
     serverParameters: {
       internalQueryFacetBufferSizeBytes: 104857600,
       internalQueryFacetMaxOutputDocSizeBytes: 104857600,
       internalLookupStageIntermediateDocumentMaxSizeBytes: 104857600,
       internalDocumentSourceGroupMaxMemoryBytes: 104857600,
       internalQueryMaxBlockingSortMemoryUsageBytes: 104857600,
       internalQueryProhibitBlockingMergeOnMongoS: 0,
       internalQueryMaxAddToSetBytes: 104857600,
       internalDocumentSourceSetWindowFieldsMaxMemoryBytes: 104857600,
       internalQueryFrameworkControl: 'trySbeRestricted'
     },
     ok: 1
   }
   ```

2. Т.к. в запросе используется условие по всем трём полям, то создаю составной индекс по всем им:
   ```
   test> db.operations.createIndex( { "date": 1 , "name": 1, "operation": 1 } )
   date_1_name_1_operation_1
   ```

3. Проверяю, что индекс в коллекции создан:
   ```
   test> db.operations.getIndexes()
   [
     { v: 2, key: { _id: 1 }, name: '_id_' },
     {
       v: 2,
       key: { date: 1, name: 1, operation: 1 },
       name: 'date_1_name_1_operation_1'
     }
   ]
   ```

4. Получаю статистику выполнения запроса после создания индекса:
   ```
   test> db.operations.find( { $and: [ { name: "Сидор Сидоров"}, { date: { $gte: "2024-09-11 14:00:00" } }, { date: { $lt: "2024-09-12 14:00:00" }} ]  } ).explain("executionStats")
   {
     explainVersion: '1',
     queryPlanner: {
       namespace: 'test.operations',
       indexFilterSet: false,
       parsedQuery: {
         '$and': [
           { name: { '$eq': 'Сидор Сидоров' } },
           { date: { '$lt': '2024-09-12 14:00:00' } },
           { date: { '$gte': '2024-09-11 14:00:00' } }
         ]
       },
       queryHash: '21D08A2C',
       planCacheKey: 'F54DE899',
       maxIndexedOrSolutionsReached: false,
       maxIndexedAndSolutionsReached: false,
       maxScansToExplodeReached: false,
       winningPlan: {
         stage: 'FETCH',
         inputStage: {
           stage: 'IXSCAN',
           keyPattern: { date: 1, name: 1, operation: 1 },
           indexName: 'date_1_name_1_operation_1',
           isMultiKey: false,
           multiKeyPaths: { date: [], name: [], operation: [] },
           isUnique: false,
           isSparse: false,
           isPartial: false,
           indexVersion: 2,
           direction: 'forward',
           indexBounds: {
             date: [ '["2024-09-11 14:00:00", "2024-09-12 14:00:00")' ],
             name: [ '["Сидор Сидоров", "Сидор Сидоров"]' ],
             operation: [ '[MinKey, MaxKey]' ]
           }
         }
       },
        rejectedPlans: []
     },
     executionStats: {
       executionSuccess: true,
       nReturned: 506,
       executionTimeMillis: 3,
       totalKeysExamined: 1440,
       totalDocsExamined: 506,
       executionStages: {
         stage: 'FETCH',
         nReturned: 506,
         executionTimeMillisEstimate: 0,
         works: 1440,
         advanced: 506,
         needTime: 933,
         needYield: 0,
         saveState: 1,
         restoreState: 1,
         isEOF: 1,
         docsExamined: 506,
         alreadyHasObj: 0,
         inputStage: {
           stage: 'IXSCAN',
           nReturned: 506,
           executionTimeMillisEstimate: 0,
           works: 1440,
           advanced: 506,
           needTime: 933,
           needYield: 0,
           saveState: 1,
           restoreState: 1,
           isEOF: 1,
           keyPattern: { date: 1, name: 1, operation: 1 },
           indexName: 'date_1_name_1_operation_1',
           isMultiKey: false,
           multiKeyPaths: { date: [], name: [], operation: [] },
           isUnique: false,
           isSparse: false,
           isPartial: false,
           indexVersion: 2,
           direction: 'forward',
           indexBounds: {
             date: [ '["2024-09-11 14:00:00", "2024-09-12 14:00:00")' ],
             name: [ '["Сидор Сидоров", "Сидор Сидоров"]' ],
             operation: [ '[MinKey, MaxKey]' ]
           },
           keysExamined: 1440,
           seeks: 934,
           dupsTested: 0,
           dupsDropped: 0
         }
       }
     },
     command: {
       find: 'operations',
       filter: {
         '$and': [
           { name: 'Сидор Сидоров' },
           { date: { '$gte': '2024-09-11 14:00:00' } },
           { date: { '$lt': '2024-09-12 14:00:00' } }
         ]
       },
       '$db': 'test'
     },
     serverInfo: {
       host: 'lab1',
       port: 27017,
       version: '7.0.14',
       gitVersion: 'ce59cfc6a3c5e5c067dca0d30697edd68d4f5188'
     },
     serverParameters: {
       internalQueryFacetBufferSizeBytes: 104857600,
       internalQueryFacetMaxOutputDocSizeBytes: 104857600,
       internalLookupStageIntermediateDocumentMaxSizeBytes: 104857600,
       internalDocumentSourceGroupMaxMemoryBytes: 104857600,
       internalQueryMaxBlockingSortMemoryUsageBytes: 104857600,
       internalQueryProhibitBlockingMergeOnMongoS: 0,
       internalQueryMaxAddToSetBytes: 104857600,
       internalDocumentSourceSetWindowFieldsMaxMemoryBytes: 104857600,
       internalQueryFrameworkControl: 'trySbeRestricted'
     },
     ok: 1
   }
   ```
#### Анализ полученного результата:

До создания индекса:
```
stage: 'COLLSCAN' - полное сканирование коллекции
executionTimeMillis: 5 - время выполнения 5 мс
totalDocsExamined: 10000 - просканировано 10000 документов
nReturned: 506 - в результате получено 506 документов
```

После создания индекса:
```
stage: 'IXSCAN' - сканирование индекса
indexName: 'date_1_name_1_operation_1' - использован созданный выше индекс
executionTimeMillis: 3 - время выполнения 3 мс
totalDocsExamined: 506 - просканировано 506 документов
nReturned: 506 - в результате получено 506 документов
```

Вывод: созданный индекс работает и улучшает эффективность выполнения запроса
