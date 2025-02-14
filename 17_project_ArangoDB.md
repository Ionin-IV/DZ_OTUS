# Проектная работа по теме: "Сравнение СУБД ArangoDB, как графовой, с Neo4j, и как документоориентированной, с MongoDB"

## Цели проектной работы:

1. Провести сравнение СУБД ArangoDB, как графовой, и Neo4j.
2. Провести сравнение СУБД ArangoDB, как документоориентированной, и MongoDB.

## Стенд для тестирования

1. СУБД будут тестироваться на одной и той же ВМ со следующей спецификацией:
- процессор: 8 ядер
- ОЗУ: 8Гб
- жёсткий диск: 50Гб
- ОС: CentOS 8.5.2111
2. Версии СУБД:
- ArangoDB 3.12.3
- Neo4j 5.26.1
- MongoDB 7.0.16
3. СУБД будут тестироваться в некластерных конфигурациях.

## Генерация тестовых данных

Создаю данные заказов пользователей со следующими полями:
* order_id - номер заказа
* customer - пользователь
* date - дата и время заказа
* price - сумма заказа
* shop - магазин
* city - город
* prod - категория товара

Данные будут генерироваться параллельно в 5 потоков.

Для этого выполняю следующие действия:
1. Создаю скрипт (bash linux) data_gen.sh, генерирующий данные в json-файл(ы):
```
#!/bin/sh

# входные параметры
ALL=$1 # общее количество заказов
FROM=$2 # номера заказов от
TO=$3 # номера заказов до
FILE_NUM=$4 # номер файла

CUSTOMERS=("Ivan" "Petr" "Pavel" "Dmitry" "Aleksey" "Sergey" "Vladimir" "Victor" "Oleg" "Andrey") # массив пользователей
SHOPS=("Ozon" "WB" "Kuper" "YandexMarket") # массив магазинов
CITIES=("Moscow" "Tver" "Yaroslavl" "Vladimir" "Ryazan" "Tula" "Kaluga" "Bryansk" "Smolensk" "Kostroma") # массив городов
PRODS=("Foods" "Drink" "Cloth" "Shoes" "Hosehold" "Hobby" "AutoGoods" "Books" "Electronics" "Pharmacy") # массив категорий товаров

for (( i=$FROM; i <= $TO; i++ ))
do
        DT_REV=$(($ALL - $TO + $FROM - $i))
        DT=`date +"%F %H:%M:00" --date="$DT_REV minutes ago"` # генерация даты/времени заказа
        CUSTOMER=`tr -dc 0-9 </dev/urandom | head -c 1` # генерация случайного пользователя
        CITY=`tr -dc 0-9 </dev/urandom | head -c 1` # генерация случайного города
        SHOP=`tr -dc 0-3 </dev/urandom | head -c 1` # генерация случайного магазина
        PROD=`tr -dc 0-9 </dev/urandom | head -c 1` # генерация случаной категории заказа
        PRICE=`tr -dc 1-9 </dev/urandom | head -c 3` # генерация случайно суммы заказа

        # запись всех сгенерированных данных в один json-файл
        echo { \"order_id\": $i, \"customer\": \"${CUSTOMERS[$CUSTOMER]}\", \"date\": \"$DT\", \"price\": $PRICE, \"shop\": \"${SHOPS[$SHOP]}\", \"city\": \"${CITIES[$CITY]}\", \"prod\": \"${PRODS[$PROD]}\" } >> $FILE_NUM.json

        # запись сгенерированных данных в несколкьо json-файлов (только для загрузки данных в ArangoDB в графовом виде)
        echo { \"_key\": \"$i\", \"order_id\": $i, \"date\": \"$DT\", \"price\": $PRICE } >> order_$FILE_NUM.json
        echo { \"_from\": \"customers/${CUSTOMERS[$CUSTOMER]}\", \"_to\": \"orders2/$i\" } >> customer_to_order_$FILE_NUM.json
        echo { \"_from\": \"orders2/$i\", \"_to\": \"shops/${SHOPS[$SHOP]}\" } >> order_to_shop_$FILE_NUM.json
        echo { \"_from\": \"orders2/$i\", \"_to\": \"cities/${CITIES[$CITY]}\" } >> order_to_city_$FILE_NUM.json
        echo { \"_from\": \"orders2/$i\", \"_to\": \"prods/${PRODS[$PROD]}\" } >> order_to_prods_$FILE_NUM.json
done
```

2. Запускаю параллельную генерацию 1 миллиона заказов по 200 тысяч в потоке скриптом:
```
#!/bin/sh

/root/data_gen.sh 1000000 1 200000 01 &
/root/data_gen.sh 1000000 200001 400000 02 &
/root/data_gen.sh 1000000 400001 600000 03 &
/root/data_gen.sh 1000000 600001 800000 04 &
/root/data_gen.sh 1000000 800001 1000000 05 &
```

3. Собираю сгенерированные потоками части данных в общие json-файлы:
```
cat 01.json >> orders_all.json
cat 02.json >> orders_all.json
cat 03.json >> orders_all.json
cat 04.json >> orders_all.json
cat 05.json >> orders_all.json

cat order_01.json >> orders.json
cat order_02.json >> orders.json
cat order_03.json >> orders.json
cat order_04.json >> orders.json
cat order_05.json >> orders.json

cat customer_to_order_01.json >> customer_to_order.json
cat customer_to_order_02.json >> customer_to_order.json
cat customer_to_order_03.json >> customer_to_order.json
cat customer_to_order_04.json >> customer_to_order.json
cat customer_to_order_05.json >> customer_to_order.json

cat order_to_shop_01.json >> order_to_shop.json
cat order_to_shop_02.json >> order_to_shop.json
cat order_to_shop_03.json >> order_to_shop.json
cat order_to_shop_04.json >> order_to_shop.json
cat order_to_shop_05.json >> order_to_shop.json

cat order_to_city_01.json >> order_to_city.json
cat order_to_city_02.json >> order_to_city.json
cat order_to_city_03.json >> order_to_city.json
cat order_to_city_04.json >> order_to_city.json
cat order_to_city_05.json >> order_to_city.json

cat order_to_prods_01.json >> order_to_prods.json
cat order_to_prods_02.json >> order_to_prods.json
cat order_to_prods_03.json >> order_to_prods.json
cat order_to_prods_04.json >> order_to_prods.json
cat order_to_prods_05.json >> order_to_prods.json
```

Примеры полученных данных:

* orders_all.json
```
{ "order_id": 1, "customer": "Dmitry", "date": "2023-07-24 23:11:00", "price": 945, "shop": "Kuper", "city": "Kostroma", "prod": "AutoGoods" }
{ "order_id": 2, "customer": "Aleksey", "date": "2023-07-24 23:12:00", "price": 554, "shop": "YandexMarket", "city": "Tver", "prod": "Electronics" }
{ "order_id": 3, "customer": "Victor", "date": "2023-07-24 23:13:00", "price": 748, "shop": "Ozon", "city": "Moscow", "prod": "Books" }
{ "order_id": 4, "customer": "Sergey", "date": "2023-07-24 23:14:00", "price": 621, "shop": "WB", "city": "Yaroslavl", "prod": "Cloth" }
{ "order_id": 5, "customer": "Petr", "date": "2023-07-24 23:15:00", "price": 414, "shop": "Kuper", "city": "Ryazan", "prod": "Electronics" }
```

* orders.json
```
{ "_key": "1", "order_id": 1, "date": "2023-07-24 23:11:00", "price": 945 }
{ "_key": "2", "order_id": 2, "date": "2023-07-24 23:12:00", "price": 554 }
{ "_key": "3", "order_id": 3, "date": "2023-07-24 23:13:00", "price": 748 }
{ "_key": "4", "order_id": 4, "date": "2023-07-24 23:14:00", "price": 621 }
{ "_key": "5", "order_id": 5, "date": "2023-07-24 23:15:00", "price": 414 }
```

* customer_to_order.json
```
{ "_from": "customers/Dmitry", "_to": "orders/1" }
{ "_from": "customers/Aleksey", "_to": "orders/2" }
{ "_from": "customers/Victor", "_to": "orders/3" }
{ "_from": "customers/Sergey", "_to": "orders/4" }
{ "_from": "customers/Petr", "_to": "orders/5" }
```

* order_to_shop.json
```
{ "_from": "orders/1", "_to": "shops/Kuper" }
{ "_from": "orders/2", "_to": "shops/YandexMarket" }
{ "_from": "orders/3", "_to": "shops/Ozon" }
{ "_from": "orders/4", "_to": "shops/WB" }
{ "_from": "orders/5", "_to": "shops/Kuper" }
```

* order_to_city.json
```
{ "_from": "orders/1", "_to": "cities/Kostroma" }
{ "_from": "orders/2", "_to": "cities/Tver" }
{ "_from": "orders/3", "_to": "cities/Moscow" }
{ "_from": "orders/4", "_to": "cities/Yaroslavl" }
{ "_from": "orders/5", "_to": "cities/Ryazan" }
```

* order_to_prods.json
```
{ "_from": "orders/1", "_to": "prods/AutoGoods" }
{ "_from": "orders/2", "_to": "prods/Electronics" }
{ "_from": "orders/3", "_to": "prods/Books" }
{ "_from": "orders/4", "_to": "prods/Cloth" }
{ "_from": "orders/5", "_to": "prods/Electronics" }
```

4. Создаю справочные json-файлы (для загрузки данных в ArangoDB в графовом виде):

* пользователи в customers.json:
```
{ "_key": "Ivan", "customer": "Ivan" }
{ "_key": "Petr", "customer": "Petr" }
{ "_key": "Pavel", "customer": "Pavel" }
{ "_key": "Dmitry", "customer": "Dmitry" }
{ "_key": "Aleksey", "customer": "Aleksey" }
{ "_key": "Sergey", "customer": "Sergey" }
{ "_key": "Vladimir", "customer": "Vladimir" }
{ "_key": "Victor", "customer": "Victor" }
{ "_key": "Oleg", "customer": "Oleg" }
{ "_key": "Andrey", "customer": "Andrey" }
```

* магазины в shops.json:
```
{ "_key": "Ozon", "shop": "Ozon" }
{ "_key": "WB", "shop": "WB" }
{ "_key": "Kuper", "shop": "Kuper" }
{ "_key": "YandexMarket", "shop": "YandexMarket" }
```

* города в cities.json:
```
{ "_key": "Moscow", "city": "Moscow" }
{ "_key": "Tver", "city": "Tver" }
{ "_key": "Yaroslavl", "city": "Yaroslavl" }
{ "_key": "Vladimir", "city": "Vladimir" }
{ "_key": "Ryazan", "city": "Ryazan" }
{ "_key": "Tula", "city": "Tula" }
{ "_key": "Kaluga", "city": "Kaluga" }
{ "_key": "Bryansk", "city": "Bryansk" }
{ "_key": "Smolensk", "city": "Smolensk" }
{ "_key": "Kostroma", "city": "Kostroma" }
```

* категории продуктов в prods.json:
```
{ "_key": "Foods", "prod": "Foods" }
{ "_key": "Drinks", "prod": "Drinks" }
{ "_key": "Cloth", "prod": "Cloth" }
{ "_key": "Shoes", "prod": "Shoes" }
{ "_key": "Household", "prod": "Household" }
{ "_key": "Hobby", "prod": "Hobby" }
{ "_key": "AutoGoods", "prod": "AutoGoods" }
{ "_key": "Books", "prod": "Books" }
{ "_key": "Electronics", "prod": "Electronics" }
{ "_key": "Pharmacy", "prod": "Pharmacy" }
```

## Сравнение СУБД ArangoDB, как графовой, с Neo4j

### Загрузка тестовых данных в Neo4j

1. Копирую сгенерированный ранее файл orders_all.json в директорию /var/lib/neo4j/import/

2. Пытаюсь загрузить сразу весь миллион заказов:
```
CALL apoc.load.json("file:///orders_all.json")
YIELD value
MERGE (o:order {order_id: value.order_id})
SET o.date = value.date, o.price = value.price
MERGE (cs:customer {customer: value.customer})
MERGE (s:shop {shop: value.shop})
MERGE (c:city {city: value.city})
MERGE (p:prod {prod: value.prod})
MERGE (cs)-[:CUSTOMER_TO_ORDER]->(o)
MERGE (o)-[:ORDER_TO_SHOP]->(s)
MERGE (o)-[:ORDER_TO_CITY]->(c)
MERGE (o)-[:ORDER_TO_PROD]->(p);
```
__РЕЗУЛЬТАТ__: команда висит очень долгое время (больше 5 часов) с непонятным временем выполнения. Прерываю команду.

3. Принимаю решение загружать данные частями, для чего дополнительно форматирую входной файл:
- заключаю всё сожедржимое файла в скобки "[]" в начале и в конце файла;
- в конце каждой строки, кроме последней, добавляю запятую.

4. Методом загрузки всё большего размера данных определяю, что оптимально загружать по 50000 заказов, чтобы можно было дождаться её выполнения. Загружаю:
```
neo4j@neo4j> CALL apoc.load.json("file:///orders_all.json", '[0:50000]', {batchSize: 1000})
             YIELD value
             MERGE (o:order {order_id: value.order_id})
             SET o.date = value.date, o.price = value.price
             MERGE (cs:customer {customer: value.customer})
             MERGE (s:shop {shop: value.shop})
             MERGE (c:city {city: value.city})
             MERGE (p:prod {prod: value.prod})
             MERGE (cs)-[:CUSTOMER_TO_ORDER]->(o)
             MERGE (o)-[:ORDER_TO_SHOP]->(s)
             MERGE (o)-[:ORDER_TO_CITY]->(c)
             MERGE (o)-[:ORDER_TO_PROD]->(p);
0 rows
ready to start consuming query after 468305 ms, results consumed after another 0 ms
Added 50034 nodes, Created 200000 relationships, Set 150034 properties, Added 50034 labels
```

```
neo4j@neo4j> CALL apoc.load.json("file:///orders_all.json", '[50000:100000]', {batchSize: 1000})
             YIELD value
             MERGE (o:order {order_id: value.order_id})
             SET o.date = value.date, o.price = value.price
             MERGE (cs:customer {customer: value.customer})
             MERGE (s:shop {shop: value.shop})
             MERGE (c:city {city: value.city})
             MERGE (p:prod {prod: value.prod})
             MERGE (cs)-[:CUSTOMER_TO_ORDER]->(o)
             MERGE (o)-[:ORDER_TO_SHOP]->(s)
             MERGE (o)-[:ORDER_TO_CITY]->(c)
             MERGE (o)-[:ORDER_TO_PROD]->(p);
0 rows
ready to start consuming query after 1210063 ms, results consumed after another 0 ms
Added 50000 nodes, Created 200000 relationships, Set 150000 properties, Added 50000 labels
```

```
neo4j@neo4j> CALL apoc.load.json("file:///orders_all.json", '[100000:150000]', {batchSize: 1000})
             YIELD value
             MERGE (o:order {order_id: value.order_id})
             SET o.date = value.date, o.price = value.price
             MERGE (cs:customer {customer: value.customer})
             MERGE (s:shop {shop: value.shop})
             MERGE (c:city {city: value.city})
             MERGE (p:prod {prod: value.prod})
             MERGE (cs)-[:CUSTOMER_TO_ORDER]->(o)
             MERGE (o)-[:ORDER_TO_SHOP]->(s)
             MERGE (o)-[:ORDER_TO_CITY]->(c)
             MERGE (o)-[:ORDER_TO_PROD]->(p);
0 rows
ready to start consuming query after 1933327 ms, results consumed after another 0 ms
Added 50000 nodes, Created 200000 relationships, Set 150000 properties, Added 50000 labels
```

```
neo4j@neo4j> CALL apoc.load.json("file:///orders_all.json", '[150000:200000]', {batchSize: 1000})
             YIELD value
             MERGE (o:order {order_id: value.order_id})
             SET o.date = value.date, o.price = value.price
             MERGE (cs:customer {customer: value.customer})
             MERGE (s:shop {shop: value.shop})
             MERGE (c:city {city: value.city})
             MERGE (p:prod {prod: value.prod})
             MERGE (cs)-[:CUSTOMER_TO_ORDER]->(o)
             MERGE (o)-[:ORDER_TO_SHOP]->(s)
             MERGE (o)-[:ORDER_TO_CITY]->(c)
             MERGE (o)-[:ORDER_TO_PROD]->(p);
0 rows
ready to start consuming query after 2644656 ms, results consumed after another 0 ms
Added 50000 nodes, Created 200000 relationships, Set 150000 properties, Added 50000 labels
```

```
neo4j@neo4j> CALL apoc.load.json("file:///orders_all.json", '[200000:250000]', {batchSize: 1000})
             YIELD value
             MERGE (o:order {order_id: value.order_id})
             SET o.date = value.date, o.price = value.price
             MERGE (cs:customer {customer: value.customer})
             MERGE (s:shop {shop: value.shop})
             MERGE (c:city {city: value.city})
             MERGE (p:prod {prod: value.prod})
             MERGE (cs)-[:CUSTOMER_TO_ORDER]->(o)
             MERGE (o)-[:ORDER_TO_SHOP]->(s)
             MERGE (o)-[:ORDER_TO_CITY]->(c)
             MERGE (o)-[:ORDER_TO_PROD]->(p);
0 rows
ready to start consuming query after 3517802 ms, results consumed after another 1 ms
Added 50000 nodes, Created 200000 relationships, Set 150002 properties, Added 50000 labels
```

__РЕЗУЛЬТАТ__: загрузка каждых следующих 50000 заказов идёт всё дольше. Скорее всего это связано с тем, что не только загружаются новые данные, но и они связываются с уже имющимися в БД.
Расчёт по росту времени загрузки каждой следующей порции показывает, что полная загрузка будет длиться около 42 часов. Это объясняет долгое зависание первой загрузки полного набора данных. Но ждать 43 часа не разумно, поэтому решаю остановиться на загруженных 250000 заказов.

### Загрузка тестовых данных в ArangoDB

__ПРИМЕЧАНИЕ__: так как в Neo4j удалось загрузить за адекватный период времени только 250000 заказов, то и в ArangoDB загрузим такое же количество, предварительно урезав данные в json-файлах.

1. Захожу в консоль:
```
arangosh
```
Примечание: так же есть web-консоль по адресу http://127.0.0.1:8529

2. Создаю тестовую БД:
```
db._createDatabase("test");
```

3. Перехожу в созданную БД:
```
db._useDatabase("test");
```

4. Создаю коллекции узлов:
```
127.0.0.1:8529@test> db._create("orders")
db._createEdgeCollection("order_to_shop");
[ArangoCollection 113042, "orders" (type document, status loaded)]

127.0.0.1:8529@test> db._create("customers")
[ArangoCollection 113047, "customers" (type document, status loaded)]

127.0.0.1:8529@test> db._create("shops")
[ArangoCollection 113052, "shops" (type document, status loaded)]

127.0.0.1:8529@test> db._create("cities")
[ArangoCollection 113057, "cities" (type document, status loaded)]

127.0.0.1:8529@test> db._create("prods")
[ArangoCollection 113062, "prods" (type document, status loaded)]
```

5. Создаю коллекции связей:
```
127.0.0.1:8529@test> db._createEdgeCollection("customer_to_order");
[ArangoCollection 113067, "customer_to_order" (type edge, status loaded)]

127.0.0.1:8529@test> db._createEdgeCollection("order_to_city");
[ArangoCollection 113074, "order_to_city" (type edge, status loaded)]

127.0.0.1:8529@test> db._createEdgeCollection("order_to_prods");
[ArangoCollection 113081, "order_to_prods" (type edge, status loaded)]

127.0.0.1:8529@test> db._createEdgeCollection("order_to_shop");
[ArangoCollection 113088, "order_to_shop" (type edge, status loaded)]
```

6. Создаю граф:
```
127.0.0.1:8529@test> var graph_module =  require("org/arangodb/general-graph");

127.0.0.1:8529@test> var edgeDefinitions = [ { collection: "customer_to_order", "from": [ "customers" ], "to" : [ "orders" ] }, { collection: "order_to_city", "from": [ "orders" ], "to" : [ "cities" ] }, { collection: "order_to_prods", "from": [ "orders" ], "to" : [ "prods" ] }, { collection: "order_to_shop", "from": [ "orders" ], "to" : [ "shops" ] } ];

127.0.0.1:8529@test> graph = graph_module._create("orders_graph", edgeDefinitions);
{[GeneralGraph]
  "customer_to_order" : [ArangoCollection 113067, "customer_to_order" (type edge, status loaded)],
  "customers" : [ArangoCollection 113047, "customers" (type document, status loaded)],
  "orders" : [ArangoCollection 113042, "orders" (type document, status loaded)],
  "order_to_city" : [ArangoCollection 113074, "order_to_city" (type edge, status loaded)],
  "cities" : [ArangoCollection 113057, "cities" (type document, status loaded)],
  "order_to_prods" : [ArangoCollection 113081, "order_to_prods" (type edge, status loaded)],
  "prods" : [ArangoCollection 113062, "prods" (type document, status loaded)],
  "order_to_shop" : [ArangoCollection 113088, "order_to_shop" (type edge, status loaded)],
  "shops" : [ArangoCollection 113052, "shops" (type document, status loaded)]
}
```

7. Загружаю сгенерированные в json-файлы данные в созданные колекции:
```
[root@test ~]# arangoimport --file "/tmp/order_customers.json" --type json --collection "customers" --server.database "test"
Please specify a password:
2025-02-11T08:19:17.498137Z [5132-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             customers
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        /tmp/order_customers.json
file type:              json
threads:                8
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...

created:          10
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@test ~]# arangoimport --file "/tmp/order_shops.json" --type json --collection "shops" --server.database "test"
Please specify a password:
2025-02-11T08:19:27.362108Z [5144-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             shops
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        /tmp/order_shops.json
file type:              json
threads:                8
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...

created:          4
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@test ~]# arangoimport --file "/tmp/order_cities.json" --type json --collection "cities" --server.database "test"
Please specify a password:
2025-02-11T08:19:35.978207Z [5155-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             cities
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        /tmp/order_cities.json
file type:              json
threads:                8
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...

created:          10
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@test ~]# arangoimport --file "/tmp/order_prods.json" --type json --collection "prods" --server.database "test"
Please specify a password:
2025-02-11T08:19:44.234143Z [5166-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             prods
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        /tmp/order_prods.json
file type:              json
threads:                8
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...

created:          10
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@test ~]# arangoimport --file "/tmp/orders.json" --type json --collection "orders" --server.database "test"
Please specify a password:
2025-02-11T08:19:52.610229Z [5177-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             orders
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        /tmp/orders.json
file type:              json
threads:                8
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...
2025-02-11T08:19:52.611622Z [5177-1] INFO [9ddf3] {general} processed 1.0 MB (3%) of input file
2025-02-11T08:19:52.612339Z [5177-1] INFO [9ddf3] {general} processed 2.0 MB (7%) of input file
2025-02-11T08:19:52.613375Z [5177-1] INFO [9ddf3] {general} processed 3.1 MB (12%) of input file
2025-02-11T08:19:52.613708Z [5177-1] INFO [9ddf3] {general} processed 4.1 MB (17%) of input file
2025-02-11T08:19:52.614046Z [5177-1] INFO [9ddf3] {general} processed 5.2 MB (22%) of input file
2025-02-11T08:19:52.615903Z [5177-1] INFO [9ddf3] {general} processed 6.2 MB (27%) of input file
2025-02-11T08:19:52.616248Z [5177-1] INFO [9ddf3] {general} processed 7.3 MB (32%) of input file
2025-02-11T08:19:52.616563Z [5177-1] INFO [9ddf3] {general} processed 8.3 MB (37%) of input file
2025-02-11T08:19:52.619357Z [5177-1] INFO [9ddf3] {general} processed 9.4 MB (42%) of input file
2025-02-11T08:19:52.623965Z [5177-1] INFO [9ddf3] {general} processed 10.4 MB (47%) of input file
2025-02-11T08:19:52.624187Z [5177-1] INFO [9ddf3] {general} processed 11.5 MB (52%) of input file
2025-02-11T08:19:52.624440Z [5177-1] INFO [9ddf3] {general} processed 12.5 MB (57%) of input file
2025-02-11T08:19:52.624760Z [5177-1] INFO [9ddf3] {general} processed 13.6 MB (62%) of input file
2025-02-11T08:19:52.624993Z [5177-1] INFO [9ddf3] {general} processed 14.6 MB (67%) of input file
2025-02-11T08:19:52.625206Z [5177-1] INFO [9ddf3] {general} processed 15.7 MB (71%) of input file
2025-02-11T08:19:52.625426Z [5177-1] INFO [9ddf3] {general} processed 16.7 MB (76%) of input file
2025-02-11T08:19:52.625669Z [5177-1] INFO [9ddf3] {general} processed 17.8 MB (81%) of input file
2025-02-11T08:19:52.631058Z [5177-1] INFO [9ddf3] {general} processed 18.8 MB (86%) of input file
2025-02-11T08:19:52.631368Z [5177-1] INFO [9ddf3] {general} processed 19.9 MB (91%) of input file
2025-02-11T08:19:52.631749Z [5177-1] INFO [9ddf3] {general} processed 20.9 MB (96%) of input file

created:          250000
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@test ~]# arangoimport --file "/tmp/customer_to_order.json" --type json --collection "customer_to_order" --server.database "test"
Please specify a password:
2025-02-11T08:21:45.482377Z [5210-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             customer_to_order
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        /tmp/customer_to_order.json
file type:              json
threads:                8
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...
2025-02-11T08:21:45.483857Z [5210-1] INFO [9ddf3] {general} processed 1.0 MB (3%) of input file
2025-02-11T08:21:45.484568Z [5210-1] INFO [9ddf3] {general} processed 2.0 MB (10%) of input file
2025-02-11T08:21:45.485784Z [5210-1] INFO [9ddf3] {general} processed 3.1 MB (18%) of input file
2025-02-11T08:21:45.486230Z [5210-1] INFO [9ddf3] {general} processed 4.1 MB (25%) of input file
2025-02-11T08:21:45.486690Z [5210-1] INFO [9ddf3] {general} processed 5.2 MB (33%) of input file
2025-02-11T08:21:45.488601Z [5210-1] INFO [9ddf3] {general} processed 6.2 MB (41%) of input file
2025-02-11T08:21:45.489007Z [5210-1] INFO [9ddf3] {general} processed 7.3 MB (48%) of input file
2025-02-11T08:21:45.489371Z [5210-1] INFO [9ddf3] {general} processed 8.3 MB (56%) of input file
2025-02-11T08:21:45.492020Z [5210-1] INFO [9ddf3] {general} processed 9.4 MB (63%) of input file
2025-02-11T08:21:45.496565Z [5210-1] INFO [9ddf3] {general} processed 10.4 MB (71%) of input file
2025-02-11T08:21:45.496891Z [5210-1] INFO [9ddf3] {general} processed 11.5 MB (79%) of input file
2025-02-11T08:21:45.497194Z [5210-1] INFO [9ddf3] {general} processed 12.5 MB (86%) of input file
2025-02-11T08:21:45.497426Z [5210-1] INFO [9ddf3] {general} processed 13.6 MB (94%) of input file

created:          250000
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@test ~]# arangoimport --file "/tmp/order_to_city.json" --type json --collection "order_to_city" --server.database "test"
Please specify a password:
2025-02-11T08:21:57.906383Z [5223-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             order_to_city
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        /tmp/order_to_city.json
file type:              json
threads:                8
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...
2025-02-11T08:21:57.907760Z [5223-1] INFO [9ddf3] {general} processed 1.0 MB (3%) of input file
2025-02-11T08:21:57.908430Z [5223-1] INFO [9ddf3] {general} processed 2.0 MB (10%) of input file
2025-02-11T08:21:57.909377Z [5223-1] INFO [9ddf3] {general} processed 3.1 MB (18%) of input file
2025-02-11T08:21:57.909805Z [5223-1] INFO [9ddf3] {general} processed 4.1 MB (26%) of input file
2025-02-11T08:21:57.910122Z [5223-1] INFO [9ddf3] {general} processed 5.2 MB (34%) of input file
2025-02-11T08:21:57.912087Z [5223-1] INFO [9ddf3] {general} processed 6.2 MB (42%) of input file
2025-02-11T08:21:57.912413Z [5223-1] INFO [9ddf3] {general} processed 7.3 MB (50%) of input file
2025-02-11T08:21:57.912712Z [5223-1] INFO [9ddf3] {general} processed 8.3 MB (58%) of input file
2025-02-11T08:21:57.915601Z [5223-1] INFO [9ddf3] {general} processed 9.4 MB (66%) of input file
2025-02-11T08:21:57.920239Z [5223-1] INFO [9ddf3] {general} processed 10.4 MB (74%) of input file
2025-02-11T08:21:57.920489Z [5223-1] INFO [9ddf3] {general} processed 11.5 MB (81%) of input file
2025-02-11T08:21:57.920735Z [5223-1] INFO [9ddf3] {general} processed 12.5 MB (89%) of input file
2025-02-11T08:21:57.920892Z [5223-1] INFO [9ddf3] {general} processed 13.2 MB (97%) of input file

created:          250000
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@test ~]# arangoimport --file "/tmp/order_to_prods.json" --type json --collection "order_to_prods" --server.database "test"
Please specify a password:
2025-02-11T08:22:09.922326Z [5235-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             order_to_prods
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        /tmp/order_to_prods.json
file type:              json
threads:                8
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...
2025-02-11T08:22:09.923786Z [5235-1] INFO [9ddf3] {general} processed 1.0 MB (3%) of input file
2025-02-11T08:22:09.924488Z [5235-1] INFO [9ddf3] {general} processed 2.0 MB (11%) of input file
2025-02-11T08:22:09.925712Z [5235-1] INFO [9ddf3] {general} processed 3.1 MB (19%) of input file
2025-02-11T08:22:09.926054Z [5235-1] INFO [9ddf3] {general} processed 4.1 MB (27%) of input file
2025-02-11T08:22:09.926381Z [5235-1] INFO [9ddf3] {general} processed 5.2 MB (35%) of input file
2025-02-11T08:22:09.928556Z [5235-1] INFO [9ddf3] {general} processed 6.2 MB (43%) of input file
2025-02-11T08:22:09.928962Z [5235-1] INFO [9ddf3] {general} processed 7.3 MB (51%) of input file
2025-02-11T08:22:09.929303Z [5235-1] INFO [9ddf3] {general} processed 8.3 MB (59%) of input file
2025-02-11T08:22:09.932637Z [5235-1] INFO [9ddf3] {general} processed 9.4 MB (67%) of input file
2025-02-11T08:22:09.938423Z [5235-1] INFO [9ddf3] {general} processed 10.4 MB (75%) of input file
2025-02-11T08:22:09.938685Z [5235-1] INFO [9ddf3] {general} processed 11.5 MB (83%) of input file
2025-02-11T08:22:09.938937Z [5235-1] INFO [9ddf3] {general} processed 12.5 MB (91%) of input file
2025-02-11T08:22:09.939051Z [5235-1] INFO [9ddf3] {general} processed 13.0 MB (99%) of input file

created:          250000
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@test ~]# arangoimport --file "/tmp/order_to_shop.json" --type json --collection "order_to_shop" --server.database "test"
Please specify a password:
2025-02-11T08:22:21.354239Z [5249-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             order_to_shop
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        /tmp/order_to_shop.json
file type:              json
threads:                8
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...
2025-02-11T08:22:21.355711Z [5249-1] INFO [9ddf3] {general} processed 1.0 MB (3%) of input file
2025-02-11T08:22:21.356439Z [5249-1] INFO [9ddf3] {general} processed 2.0 MB (11%) of input file
2025-02-11T08:22:21.357395Z [5249-1] INFO [9ddf3] {general} processed 3.1 MB (19%) of input file
2025-02-11T08:22:21.357746Z [5249-1] INFO [9ddf3] {general} processed 4.1 MB (27%) of input file
2025-02-11T08:22:21.358096Z [5249-1] INFO [9ddf3] {general} processed 5.2 MB (35%) of input file
2025-02-11T08:22:21.359937Z [5249-1] INFO [9ddf3] {general} processed 6.2 MB (43%) of input file
2025-02-11T08:22:21.360319Z [5249-1] INFO [9ddf3] {general} processed 7.3 MB (52%) of input file
2025-02-11T08:22:21.360636Z [5249-1] INFO [9ddf3] {general} processed 8.3 MB (60%) of input file
2025-02-11T08:22:21.363570Z [5249-1] INFO [9ddf3] {general} processed 9.4 MB (68%) of input file
2025-02-11T08:22:21.368452Z [5249-1] INFO [9ddf3] {general} processed 10.4 MB (76%) of input file
2025-02-11T08:22:21.368670Z [5249-1] INFO [9ddf3] {general} processed 11.5 MB (84%) of input file
2025-02-11T08:22:21.369017Z [5249-1] INFO [9ddf3] {general} processed 12.5 MB (92%) of input file

created:          250000
warnings/errors:  0
updated/replaced: 0
ignored:          0
```

__РЕЗУЛЬТАТ__: 250000 заказов загружено за доли секунд (исключаяя подготовку данных и сам запуск команд).

### Сравнение запросов в ArangoDB и Neo4j

#### Запрос №1

__Задача__: выбрать заказы пользователя Сергей в городе Москва в промежуток веремени с 2024-01-01 09:00 по 2024-01-01 12:00.

Запрос в Neo4j
```
neo4j@neo4j> MATCH (cs:customer {customer:'Sergey'}) -[r1:CUSTOMER_TO_ORDER]- (o:order) -[r2:ORDER_TO_CITY]- (c:city {city:'Moscow'})
             WHERE o.date >= '2024-01-01 09:00' AND o.date < '2024-01-01 12:00'
             RETURN cs.customer, o.order_id, o.date, o.price ORDER BY o.date;
+------------------------------------------------------------+
| cs.customer | o.order_id | o.date                | o.price |
+------------------------------------------------------------+
| "Sergey"    | 231041     | "2024-01-01 10:54:00" | 521     |
| "Sergey"    | 231075     | "2024-01-01 11:28:00" | 892     |
+------------------------------------------------------------+

2 rows
ready to start consuming query after 537 ms, results consumed after another 192 ms
```

Запрос в ArangoDB:
```
127.0.0.1:8529@test> db._query('FOR v, e, p IN 0..2 OUTBOUND "customers/Sergey" GRAPH "orders_graph" FILTER p.vertices[2].city == "Moscow" AND p.vertices[1].date >= "2024-01-01 09:00" AND p.vertices[1].date < "2024-01-01 12:00" SORT p.vertices[1].date RETURN { customer: p.vertices[0].customer, order_id: p.vertices[1].order_id, date: p.vertices[1].date, price: p.vertices[1].price }').getExtra()
{
  "warnings" : [ ],
  "stats" : {
    "writesExecuted" : 0,
    "writesIgnored" : 0,
    "documentLookups" : 0,
    "seeks" : 0,
    "scannedFull" : 0,
    "scannedIndex" : 50912,
    "cursorsCreated" : 4,
    "cursorsRearmed" : 68,
    "cacheHits" : 72,
    "cacheMisses" : 0,
    "filtered" : 25433,
    "httpRequests" : 0,
    "executionTime" : 0.13699541300229612,
    "peakMemoryUsage" : 4227072,
    "intermediateCommits" : 0
  }
}
```
```
127.0.0.1:8529@test> db._query('FOR v, e, p IN 0..2 OUTBOUND "customers/Sergey" GRAPH "orders_graph" FILTER p.vertices[2].city == "Moscow" AND p.vertices[1].date >= "2024-01-01 09:00" AND p.vertices[1].date < "2024-01-01 12:00" SORT p.vertices[1].date RETURN { customer: p.vertices[0].customer, order_id: p.vertices[1].order_id, date: p.vertices[1].date, price: p.vertices[1].price }').toArray()
[
  {
    "customer" : "Sergey",
    "order_id" : 231041,
    "date" : "2024-01-01 10:54:00",
    "price" : 521
  },
  {
    "customer" : "Sergey",
    "order_id" : 231075,
    "date" : "2024-01-01 11:28:00",
    "price" : 892
  }
]
```

__РЕЗУЛЬТАТ__: в Neo4j запрос выполнился за 729 мс, а в ArangoDB за 137 мс.
Судя по статистике запроса в ArangoDB, запрос использовал индексы, созданные по умолчанию (primary индекс по _key на коллекциях и edge индекс по _to, _from на edge коллекциях).

Для более честного сравнения, создаю индексы на узлах и отношениях и в Neo4j:
```
neo4j@neo4j> CREATE INDEX customer_index FOR (c:customer) ON (c.customer);
0 rows
ready to start consuming query after 55 ms, results consumed after another 0 ms
Added 1 indexes

neo4j@neo4j> CREATE INDEX city_index FOR (c:city) ON (c.city);
0 rows
ready to start consuming query after 14 ms, results consumed after another 0 ms
Added 1 indexes

neo4j@neo4j> CREATE INDEX order_index FOR (o:order) ON (o.order_id, o.date, o.price);
0 rows
ready to start consuming query after 12 ms, results consumed after another 0 ms
Added 1 indexes

neo4j@neo4j> CREATE INDEX customer_to_order_index FOR ()-[r:CUSTOMER_TO_ORDER]-() ON (r.customer_to_order);
0 rows
ready to start consuming query after 15 ms, results consumed after another 0 ms
Added 1 indexes

neo4j@neo4j> CREATE INDEX order_to_city_index FOR ()-[r:ORDER_TO_CITY]-() ON (r.order_to_city);
0 rows
ready to start consuming query after 11 ms, results consumed after another 0 ms
Added 1 indexes
```

И запускаю запрос в Neo4j ещё раз:
```
neo4j@neo4j> MATCH (cs:customer {customer:'Sergey'}) -[r1:CUSTOMER_TO_ORDER]- (o:order) -[r2:ORDER_TO_CITY]- (c:city {city:'Moscow'})
             WHERE o.date >= '2024-01-01 09:00' AND o.date < '2024-01-01 12:00'
             RETURN cs.customer, o.order_id, o.date, o.price ORDER BY o.date;
+------------------------------------------------------------+
| cs.customer | o.order_id | o.date                | o.price |
+------------------------------------------------------------+
| "Sergey"    | 231041     | "2024-01-01 10:54:00" | 521     |
| "Sergey"    | 231075     | "2024-01-01 11:28:00" | 892     |
+------------------------------------------------------------+

2 rows
ready to start consuming query after 142 ms, results consumed after another 28 ms
```

__РЕЗУЛЬТАТ__: после построения индексов в Neo4j, время выполнения запросов стало примерно сопоставимым (170 мс в Neo4j против 137 мс в ArangoDB).

#### Запрос №2

__Задача__: выбрать сумму цен заказов по категориям товаров пользователя Владимир в магазине WB за 2024-01-05.

Сразу добавлю недостающие индксы в Neo4j:
```
neo4j@neo4j> CREATE INDEX prod_index FOR (p:prod) ON (p.prod);
0 rows
ready to start consuming query after 8 ms, results consumed after another 0 ms
Added 1 indexes

neo4j@neo4j> CREATE INDEX order_to_prod_index FOR ()-[r:ORDER_TO_PROD]-() ON (r.order_to_prod);
0 rows
ready to start consuming query after 10 ms, results consumed after another 0 ms
Added 1 indexes
```

Запрос в Neo4j
```
neo4j@neo4j> MATCH (cs:customer {customer:'Vladimir'}) -[r1:CUSTOMER_TO_ORDER]- (o:order) -[r2:ORDER_TO_PROD]- (p:prod)
             WHERE o.date >= '2024-01-05 00:00' AND o.date < '2024-01-06 00:00'
             return cs.customer, p.prod, sum(o.price);
+--------------------------------------------+
| cs.customer | p.prod        | sum(o.price) |
+--------------------------------------------+
| "Vladimir"  | "Cloth"       | 10114        |
| "Vladimir"  | "Hobby"       | 7479         |
| "Vladimir"  | "Pharmacy"    | 8856         |
| "Vladimir"  | "Foods"       | 8479         |
| "Vladimir"  | "AutoGoods"   | 2568         |
| "Vladimir"  | "Books"       | 7739         |
| "Vladimir"  | "Hosehold"    | 3600         |
| "Vladimir"  | "Electronics" | 14347        |
| "Vladimir"  | "Shoes"       | 4834         |
| "Vladimir"  | "Drinks"      | 7156         |
+--------------------------------------------+

10 rows
ready to start consuming query after 77 ms, results consumed after another 22 ms
```

Запрос в ArangoDB:
```
127.0.0.1:8529@test> db._query('FOR v, e, p IN 0..2 ANY "customers/Vladimir" GRAPH "orders_graph" FILTER p.vertices[1].date >= "2024-01-05 00:00" AND p.vertices[1].date < "2024-01-06 00:00" COLLECT customers = p.vertices[0].customer, prods = p.vertices[2].prod AGGREGATE sum = sum(p.vertices[1].price) SORT prods RETURN { customers, prods, sum }').getExtra()
{
  "warnings" : [ ],
  "stats" : {
    "writesExecuted" : 0,
    "writesIgnored" : 0,
    "documentLookups" : 0,
    "seeks" : 0,
    "scannedFull" : 0,
    "scannedIndex" : 52963,
    "cursorsCreated" : 8,
    "cursorsRearmed" : 1128,
    "cacheHits" : 1135,
    "cacheMisses" : 1,
    "filtered" : 25142,
    "httpRequests" : 0,
    "executionTime" : 0.13479698999981338,
    "peakMemoryUsage" : 4194304,
    "intermediateCommits" : 0
  }
}
```
```
127.0.0.1:8529@test> db._query('FOR v, e, p IN 0..2 ANY "customers/Vladimir" GRAPH "orders_graph" FILTER p.vertices[1].date >= "2024-01-05 00:00" AND p.vertices[1].date < "2024-01-06 00:00" COLLECT customers = p.vertices[0].customer, prods = p.vertices[2].prod AGGREGATE sum = sum(p.vertices[1].price) SORT prods RETURN { customers, prods, sum }').toArray()
[
  {
    "customers" : "Vladimir",
    "prods" : null,
    "sum" : 225516
  },
  {
    "customers" : "Vladimir",
    "prods" : "AutoGoods",
    "sum" : 2568
  },
  {
    "customers" : "Vladimir",
    "prods" : "Books",
    "sum" : 7739
  },
  {
    "customers" : "Vladimir",
    "prods" : "Cloth",
    "sum" : 10114
  },
  {
    "customers" : "Vladimir",
    "prods" : "Drinks",
    "sum" : 7156
  },
  {
    "customers" : "Vladimir",
    "prods" : "Electronics",
    "sum" : 14347
  },
  {
    "customers" : "Vladimir",
    "prods" : "Foods",
    "sum" : 8479
  },
  {
    "customers" : "Vladimir",
    "prods" : "Hobby",
    "sum" : 7479
  },
  {
    "customers" : "Vladimir",
    "prods" : "Household",
    "sum" : 3600
  },
  {
    "customers" : "Vladimir",
    "prods" : "Pharmacy",
    "sum" : 8856
  },
  {
    "customers" : "Vladimir",
    "prods" : "Shoes",
    "sum" : 4834
  }
]
```

__РЕЗУЛЬТАТ__: в Neo4j запрос выполнился за 99 мс, а в ArangoDB за 135 мс.


## Сравнение СУБД ArangoDB, как документоориентированной, с MongoDB

### Загрузка тестовых данных в MongoDB

Загружаю сформированный ранее json-файл с 1000000 заказов:
```
[root@test ~]# mongoimport --collection=orders --db=test --file=orders_all.json
2025-02-13T10:46:05.135+0300    connected to: mongodb://localhost/
2025-02-13T10:46:08.135+0300    [#####...................] test.orders  28.8MB/138MB (20.9%)
2025-02-13T10:46:11.135+0300    [##########..............] test.orders  57.8MB/138MB (41.9%)
2025-02-13T10:46:14.135+0300    [###############.........] test.orders  86.4MB/138MB (62.7%)
2025-02-13T10:46:17.135+0300    [####################....] test.orders  116MB/138MB (84.0%)
2025-02-13T10:46:19.560+0300    [########################] test.orders  138MB/138MB (100.0%)
2025-02-13T10:46:19.560+0300    1000000 document(s) imported successfully. 0 document(s) failed to import.
```

__РЕЗУЛЬТАТ__: данные загружены за 15 секунд.

### Загрузка тестовых данных в ArangoDB

Загружаю тот же json-файл:
```
[root@rhel8 ~]# arangoimport --file "orders_all.json" --type json --collection "orders" --server.database "test"
Please specify a password:
2025-02-13T09:11:10.086675Z [5988-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             orders
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        orders_all.json
file type:              json
threads:                8
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...
2025-02-13T09:11:10.089782Z [5988-1] INFO [9ddf3] {general} processed 5.2 MB (3%) of input file
2025-02-13T09:11:10.094743Z [5988-1] INFO [9ddf3] {general} processed 9.4 MB (6%) of input file
2025-02-13T09:11:10.099470Z [5988-1] INFO [9ddf3] {general} processed 13.6 MB (9%) of input file
2025-02-13T09:11:10.100367Z [5988-1] INFO [9ddf3] {general} processed 17.8 MB (12%) of input file
2025-02-13T09:11:10.105824Z [5988-1] INFO [9ddf3] {general} processed 22.0 MB (15%) of input file
2025-02-13T09:11:10.106796Z [5988-1] INFO [9ddf3] {general} processed 26.2 MB (18%) of input file
2025-02-13T09:11:10.112507Z [5988-1] INFO [9ddf3] {general} processed 30.4 MB (21%) of input file
2025-02-13T09:11:10.118928Z [5988-1] INFO [9ddf3] {general} processed 35.6 MB (24%) of input file
2025-02-13T09:11:10.120112Z [5988-1] INFO [9ddf3] {general} processed 39.8 MB (27%) of input file
2025-02-13T09:11:10.128134Z [5988-1] INFO [9ddf3] {general} processed 44.0 MB (30%) of input file
2025-02-13T09:11:10.129604Z [5988-1] INFO [9ddf3] {general} processed 48.2 MB (33%) of input file
2025-02-13T09:11:10.139047Z [5988-1] INFO [9ddf3] {general} processed 52.4 MB (36%) of input file
2025-02-13T09:11:10.140360Z [5988-1] INFO [9ddf3] {general} processed 56.6 MB (39%) of input file
2025-02-13T09:11:10.147433Z [5988-1] INFO [9ddf3] {general} processed 60.8 MB (42%) of input file
2025-02-13T09:11:10.148372Z [5988-1] INFO [9ddf3] {general} processed 66.0 MB (45%) of input file
2025-02-13T09:11:10.156787Z [5988-1] INFO [9ddf3] {general} processed 70.2 MB (48%) of input file
2025-02-13T09:11:10.158167Z [5988-1] INFO [9ddf3] {general} processed 74.4 MB (51%) of input file
2025-02-13T09:11:10.895383Z [5988-1] INFO [9ddf3] {general} processed 78.6 MB (54%) of input file
2025-02-13T09:11:10.896456Z [5988-1] INFO [9ddf3] {general} processed 82.8 MB (57%) of input file
2025-02-13T09:11:10.973185Z [5988-1] INFO [9ddf3] {general} processed 87.0 MB (60%) of input file
2025-02-13T09:11:10.974239Z [5988-1] INFO [9ddf3] {general} processed 91.2 MB (63%) of input file
2025-02-13T09:11:10.990092Z [5988-1] INFO [9ddf3] {general} processed 95.4 MB (66%) of input file
2025-02-13T09:11:10.991082Z [5988-1] INFO [9ddf3] {general} processed 100.6 MB (69%) of input file
2025-02-13T09:11:11.050314Z [5988-1] INFO [9ddf3] {general} processed 104.8 MB (72%) of input file
2025-02-13T09:11:11.051116Z [5988-1] INFO [9ddf3] {general} processed 109.0 MB (75%) of input file
2025-02-13T09:11:11.194738Z [5988-1] INFO [9ddf3] {general} processed 113.2 MB (78%) of input file
2025-02-13T09:11:11.196193Z [5988-1] INFO [9ddf3] {general} processed 117.4 MB (81%) of input file
2025-02-13T09:11:11.247762Z [5988-1] INFO [9ddf3] {general} processed 121.6 MB (84%) of input file
2025-02-13T09:11:11.248558Z [5988-1] INFO [9ddf3] {general} processed 125.8 MB (87%) of input file
2025-02-13T09:11:11.364477Z [5988-1] INFO [9ddf3] {general} processed 131.0 MB (90%) of input file
2025-02-13T09:11:11.365247Z [5988-1] INFO [9ddf3] {general} processed 135.2 MB (93%) of input file
2025-02-13T09:11:11.718451Z [5988-1] INFO [9ddf3] {general} processed 139.4 MB (96%) of input file
2025-02-13T09:11:11.719515Z [5988-1] INFO [9ddf3] {general} processed 143.6 MB (99%) of input file

created:          1000000
warnings/errors:  0
updated/replaced: 0
ignored:          0
```

__РЕЗУЛЬТАТ__: данные загружены за 2 секунды.

### Сравнение запросов в ArangoDB и MongoDB

#### Запрос №1

__Задача__: выбрать заказы пользователя Олег в городе Тула в промежуток веремени с 2023-10-08 09:00 по 2023-10-08 15:00.

Запрос в MongoDB:
```
test> db.orders.find({ $and: [ { customer: "Oleg"}, { city: "Tula"}, { date: { $gte: "2023-10-08 09:00:00" } }, { date: { $lt: "2023-10-08 15:00:00" }} ]  }).sort({date: 1})
[
  {
    _id: ObjectId('67ada33ec06388e04ffb401a'),
    order_id: 108430,
    customer: 'Oleg',
    date: '2023-10-08 10:00:00',
    price: 332,
    shop: 'Ozon',
    city: 'Tula',
    prod: 'Books'
  },
  {
    _id: ObjectId('67ada33ec06388e04ffb402a'),
    order_id: 108450,
    customer: 'Oleg',
    date: '2023-10-08 10:20:00',
    price: 235,
    shop: 'Ozon',
    city: 'Tula',
    prod: 'Cloth'
  },
  {
    _id: ObjectId('67ada33ec06388e04ffb4125'),
    order_id: 108697,
    customer: 'Oleg',
    date: '2023-10-08 14:27:00',
    price: 439,
    shop: 'YandexMarket',
    city: 'Tula',
    prod: 'Foods'
  }
]
```
```
test> db.orders.find({ $and: [ { customer: "Oleg"}, { city: "Tula"}, { date: { $gte: "2023-10-08 09:00:00" } }, { date: { $lt: "2023-10-08 15:00:00" }} ]  }).sort({date: 1}).explain("executionStats")
{
  explainVersion: '1',
  queryPlanner: {
    namespace: 'test.orders',
    indexFilterSet: false,
    parsedQuery: {
      '$and': [
        { city: { '$eq': 'Tula' } },
        { customer: { '$eq': 'Oleg' } },
        { date: { '$lt': '2023-10-08 15:00:00' } },
        { date: { '$gte': '2023-10-08 09:00:00' } }
      ]
    },
    queryHash: '6627D976',
    planCacheKey: '6627D976',
    maxIndexedOrSolutionsReached: false,
    maxIndexedAndSolutionsReached: false,
    maxScansToExplodeReached: false,
    winningPlan: {
      stage: 'SORT',
      sortPattern: { date: 1 },
      memLimit: 104857600,
      type: 'simple',
      inputStage: {
        stage: 'COLLSCAN',
        filter: {
          '$and': [
            { city: { '$eq': 'Tula' } },
            { customer: { '$eq': 'Oleg' } },
            { date: { '$lt': '2023-10-08 15:00:00' } },
            { date: { '$gte': '2023-10-08 09:00:00' } }
          ]
        },
        direction: 'forward'
      }
    },
    rejectedPlans: []
  },
  executionStats: {
    executionSuccess: true,
    nReturned: 3,
    executionTimeMillis: 458,
    totalKeysExamined: 0,
    totalDocsExamined: 1000000,
    executionStages: {
      stage: 'SORT',
      nReturned: 3,
      executionTimeMillisEstimate: 6,
      works: 1000005,
      advanced: 3,
      needTime: 1000001,
      needYield: 0,
      saveState: 1000,
      restoreState: 1000,
      isEOF: 1,
      sortPattern: { date: 1 },
      memLimit: 104857600,
      type: 'simple',
      totalDataSizeSorted: 635,
      usedDisk: false,
      spills: 0,
      spilledDataStorageSize: 0,
      inputStage: {
        stage: 'COLLSCAN',
        filter: {
          '$and': [
            { city: { '$eq': 'Tula' } },
            { customer: { '$eq': 'Oleg' } },
            { date: { '$lt': '2023-10-08 15:00:00' } },
            { date: { '$gte': '2023-10-08 09:00:00' } }
          ]
        },
        nReturned: 3,
        executionTimeMillisEstimate: 6,
        works: 1000001,
        advanced: 3,
        needTime: 999997,
        needYield: 0,
        saveState: 1000,
        restoreState: 1000,
        isEOF: 1,
        direction: 'forward',
        docsExamined: 1000000
      }
    }
  },
  command: {
    find: 'orders',
    filter: {
      '$and': [
        { customer: 'Oleg' },
        { city: 'Tula' },
        { date: { '$gte': '2023-10-08 09:00:00' } },
        { date: { '$lt': '2023-10-08 15:00:00' } }
      ]
    },
    sort: { date: 1 },
    '$db': 'test'
  },
  serverInfo: {
    host: 'rhel8',
    port: 27017,
    version: '7.0.16',
    gitVersion: '18b949444cfdaa88e30b0e10243bc18268251c1f'
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

Запрос в ArangoDB:
```
127.0.0.1:8529@test> db._query('FOR doc IN orders FILTER doc.date >= "2023-10-08 09:00:00" AND doc.date <= "2023-10-08 15:00:00" AND doc.customer == "Oleg" AND doc.city == "Tula" RETURN doc').toArray()
[
  {
    "_key" : "10413791",
    "_id" : "orders/10413791",
    "_rev" : "_jN4Rheq-BJ",
    "order_id" : 108430,
    "customer" : "Oleg",
    "date" : "2023-10-08 10:00:00",
    "price" : 332,
    "shop" : "Ozon",
    "city" : "Tula",
    "prod" : "Books"
  },
  {
    "_key" : "10413915",
    "_id" : "orders/10413915",
    "_rev" : "_jN4Rheq-DE",
    "order_id" : 108450,
    "customer" : "Oleg",
    "date" : "2023-10-08 10:20:00",
    "price" : 235,
    "shop" : "Ozon",
    "city" : "Tula",
    "prod" : "Cloth"
  },
  {
    "_key" : "10415573",
    "_id" : "orders/10415573",
    "_rev" : "_jN4Rhey-G3",
    "order_id" : 108697,
    "customer" : "Oleg",
    "date" : "2023-10-08 14:27:00",
    "price" : 439,
    "shop" : "YandexMarket",
    "city" : "Tula",
    "prod" : "Foods"
  }
]
```
```
127.0.0.1:8529@test> db._query('FOR doc IN orders FILTER doc.date >= "2023-10-08 09:00:00" AND doc.date <= "2023-10-08 15:00:00" AND doc.customer == "Oleg" AND doc.city == "Tula" RETURN doc').getExtra()
{
  "warnings" : [ ],
  "stats" : {
    "writesExecuted" : 0,
    "writesIgnored" : 0,
    "documentLookups" : 0,
    "seeks" : 0,
    "scannedFull" : 1000000,
    "scannedIndex" : 0,
    "cursorsCreated" : 0,
    "cursorsRearmed" : 0,
    "cacheHits" : 0,
    "cacheMisses" : 0,
    "filtered" : 999997,
    "httpRequests" : 0,
    "executionTime" : 0.45731531899946276,
    "peakMemoryUsage" : 0,
    "intermediateCommits" : 0
  }
}
```

__РЕЗУЛЬТАТ__: время выполнения запроса практически идентичное (458 и 457 мс, соответственно).

Попробую пострить индексы.

Создаю индекс в MongoDB:
```
test> db.orders.createIndex( { "customer": 1 , "city": 1, "date": 1 } );
customer_1_city_1_date_1
```

Создаю индекс в ArangoDB:
```
127.0.0.1:8529@test> db.orders.ensureIndex({ type: "persistent", fields: [ "customer", "city", "date" ] });
{
  "cacheEnabled" : false,
  "deduplicate" : true,
  "estimates" : true,
  "fields" : [
    "customer",
    "city",
    "date"
  ],
  "id" : "orders/11138754",
  "isNewlyCreated" : true,
  "name" : "idx_1823934339584360448",
  "selectivityEstimate" : 1,
  "sparse" : false,
  "type" : "persistent",
  "unique" : false,
  "code" : 201
}
```

Снова выполняю запрос в MongoDB:
```
test> db.orders.find({ $and: [ { customer: "Oleg"}, { city: "Tula"}, { date: { $gte: "2023-10-08 09:00:00" } }, { date: { $lt: "2023-10-08 15:00:00" }} ]  }).sort({date: 1}).explain("executionStats");
{
  explainVersion: '1',
  queryPlanner: {
    namespace: 'test.orders',
    indexFilterSet: false,
    parsedQuery: {
      '$and': [
        { city: { '$eq': 'Tula' } },
        { customer: { '$eq': 'Oleg' } },
        { date: { '$lt': '2023-10-08 15:00:00' } },
        { date: { '$gte': '2023-10-08 09:00:00' } }
      ]
    },
    queryHash: '6627D976',
    planCacheKey: 'D37A1B8F',
    maxIndexedOrSolutionsReached: false,
    maxIndexedAndSolutionsReached: false,
    maxScansToExplodeReached: false,
    winningPlan: {
      stage: 'FETCH',
      inputStage: {
        stage: 'IXSCAN',
        keyPattern: { customer: 1, city: 1, date: 1 },
        indexName: 'customer_1_city_1_date_1',
        isMultiKey: false,
        multiKeyPaths: { customer: [], city: [], date: [] },
        isUnique: false,
        isSparse: false,
        isPartial: false,
        indexVersion: 2,
        direction: 'forward',
        indexBounds: {
          customer: [ '["Oleg", "Oleg"]' ],
          city: [ '["Tula", "Tula"]' ],
          date: [ '["2023-10-08 09:00:00", "2023-10-08 15:00:00")' ]
        }
      }
    },
    rejectedPlans: []
  },
  executionStats: {
    executionSuccess: true,
    nReturned: 3,
    executionTimeMillis: 1,
    totalKeysExamined: 3,
    totalDocsExamined: 3,
    executionStages: {
      stage: 'FETCH',
      nReturned: 3,
      executionTimeMillisEstimate: 0,
      works: 4,
      advanced: 3,
      needTime: 0,
      needYield: 0,
      saveState: 0,
      restoreState: 0,
      isEOF: 1,
      docsExamined: 3,
      alreadyHasObj: 0,
      inputStage: {
        stage: 'IXSCAN',
        nReturned: 3,
        executionTimeMillisEstimate: 0,
        works: 4,
        advanced: 3,
        needTime: 0,
        needYield: 0,
        saveState: 0,
        restoreState: 0,
        isEOF: 1,
        keyPattern: { customer: 1, city: 1, date: 1 },
        indexName: 'customer_1_city_1_date_1',
        isMultiKey: false,
        multiKeyPaths: { customer: [], city: [], date: [] },
        isUnique: false,
        isSparse: false,
        isPartial: false,
        indexVersion: 2,
        direction: 'forward',
        indexBounds: {
          customer: [ '["Oleg", "Oleg"]' ],
          city: [ '["Tula", "Tula"]' ],
          date: [ '["2023-10-08 09:00:00", "2023-10-08 15:00:00")' ]
        },
        keysExamined: 3,
        seeks: 1,
        dupsTested: 0,
        dupsDropped: 0
      }
    }
  },
  command: {
    find: 'orders',
    filter: {
      '$and': [
        { customer: 'Oleg' },
        { city: 'Tula' },
        { date: { '$gte': '2023-10-08 09:00:00' } },
        { date: { '$lt': '2023-10-08 15:00:00' } }
      ]
    },
    sort: { date: 1 },
    '$db': 'test'
  },
  serverInfo: {
    host: 'rhel8',
    port: 27017,
    version: '7.0.16',
    gitVersion: '18b949444cfdaa88e30b0e10243bc18268251c1f'
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

И в ArangoDB:
```
127.0.0.1:8529@test> db._query('FOR doc IN orders FILTER doc.date >= "2023-10-08 09:00:00" AND doc.date <= "2023-10-08 15:00:00" AND doc.customer == "Oleg" AND doc.city == "Tula" RETURN doc').getExtra()
{
  "warnings" : [ ],
  "stats" : {
    "writesExecuted" : 0,
    "writesIgnored" : 0,
    "documentLookups" : 3,
    "seeks" : 0,
    "scannedFull" : 0,
    "scannedIndex" : 3,
    "cursorsCreated" : 1,
    "cursorsRearmed" : 0,
    "cacheHits" : 0,
    "cacheMisses" : 0,
    "filtered" : 0,
    "httpRequests" : 0,
    "executionTime" : 0.0004009320000477601,
    "peakMemoryUsage" : 32768,
    "intermediateCommits" : 0
  }
}
```

__РЕЗУЛЬТАТ__: скокрость выполнения запроса в обеих БД многократно увеличилась и стала равна примерно 1 мс.

#### Запрос №2

__Задача__: выбрать сумму цен заказов по категориям товаров пользователя Иван с 2023-10-08 09:00 по 2023-10-08 15:00.

Выполняю запрос в MongoDB:
```
test> db.orders.aggregate([
... { $match: { $and: [ { customer: "Ivan"}, { date: { $gte: "2023-10-08 09:00:00" } }, { date: { $lt: "2023-10-08 15:00:00" }} ] } },
... { $group: { _id: { prod: "$prod" }, totalSum: { $sum: "$price" } }},
... { $sort: { _id: 1 }}
... ]);
[
  { _id: { prod: 'AutoGoods' }, totalSum: 1374 },
  { _id: { prod: 'Books' }, totalSum: 2325 },
  { _id: { prod: 'Cloth' }, totalSum: 2644 },
  { _id: { prod: 'Drinks' }, totalSum: 983 },
  { _id: { prod: 'Foods' }, totalSum: 3464 },
  { _id: { prod: 'Hobby' }, totalSum: 2345 },
  { _id: { prod: 'Hosehold' }, totalSum: 492 },
  { _id: { prod: 'Pharmacy' }, totalSum: 3540 },
  { _id: { prod: 'Shoes' }, totalSum: 3182 }
]
```
```
test> db.orders.aggregate([
... { $match: { $and: [ { customer: "Ivan"}, { date: { $gte: "2023-10-08 09:00:00" } }, { date: { $lt: "2023-10-08 15:00:00" }} ] } },
... { $group: { _id: { prod: "$prod" }, totalSum: { $sum: "$price" } }},
... { $sort: { _id: 1 }}
... ]).explain("executionStats");
{
  explainVersion: '2',
  stages: [
    {
      '$cursor': {
        queryPlanner: {
          namespace: 'test.orders',
          indexFilterSet: false,
          parsedQuery: {
            '$and': [
              { customer: { '$eq': 'Ivan' } },
              { date: { '$lt': '2023-10-08 15:00:00' } },
              { date: { '$gte': '2023-10-08 09:00:00' } }
            ]
          },
          queryHash: '74CC37FE',
          planCacheKey: '0E79BBFD',
          maxIndexedOrSolutionsReached: false,
          maxIndexedAndSolutionsReached: false,
          maxScansToExplodeReached: false,
          winningPlan: {
            queryPlan: {
              stage: 'GROUP',
              planNodeId: 4,
              inputStage: {
                stage: 'FETCH',
                planNodeId: 2,
                inputStage: {
                  stage: 'IXSCAN',
                  planNodeId: 1,
                  keyPattern: { customer: 1, city: 1, date: 1 },
                  indexName: 'customer_1_city_1_date_1',
                  isMultiKey: false,
                  multiKeyPaths: { customer: [], city: [], date: [] },
                  isUnique: false,
                  isSparse: false,
                  isPartial: false,
                  indexVersion: 2,
                  direction: 'forward',
                  indexBounds: {
                    customer: [ '["Ivan", "Ivan"]' ],
                    city: [ '[MinKey, MaxKey]' ],
                    date: [
                      '["2023-10-08 09:00:00", "2023-10-08 15:00:00")'
                    ]
                  }
                }
              }
            },
            slotBasedPlan: {
              slots: `$$RESULT=s34 env: { s24 = true, s2 = Nothing (SEARCH_META), s3 = 1739437287603 (NOW), s5 = IndexBounds("field #0['customer']: [CollationKey(0x4976616e), CollationKey(0x4976616e)], field #1['city']: [MinKey, MaxKey], field #2['date']: [CollationKey(0x323032332d3130"...), s1 = TimeZoneDatabase(Atlantic/Faroe...America/Managua) (timeZoneDB), s9 = {"customer" : 1, "city" : 1, "date" : 1}, s13 = Nothing }`,
              stages: '[4] project [s34 = newObj("_id", s32, "totalSum", s33)] \n' +
                '[4] project [s32 = newObj("prod", s29), s33 = doubleDoubleSumFinalize(s30)] \n' +
                '[4] group [s29] [s30 = aggDoubleDoubleSum(s27)] spillSlots[s31] mergingExprs[aggMergeDoubleDoubleSums(s31)] \n' +
                '[4] project [s29 = (s28 ?: null)] \n' +
                '[2] nlj inner [] [s19, s20, s21, s22, s23] \n' +
                '    left \n' +
                '        [1] branch {s24} [s19, s20, s21, s22, s23] \n' +
                '        [s4, s6, s7, s8, s9] [1] ixscan_generic s5 s8 s4 s6 s7 lowPriority [] @"04f108c1-b995-43e6-9914-8f9f25adca43" @"customer_1_city_1_date_1" true \n' +
                '        [s10, s16, s17, s18, s9] [1] nlj inner [] [s11, s12] \n' +
                '            left \n' +
                '                [1] project [s11 = getField(s14, "l"), s12 = getField(s14, "h")] \n' +
                '                [1] unwind s14 s15 s13 false \n' +
                '                [1] limit 1ll \n' +
                '                [1] coscan \n' +
                '            right \n' +
                '                [1] ixseek s11 s12 s18 s10 s16 s17 [] @"04f108c1-b995-43e6-9914-8f9f25adca43" @"customer_1_city_1_date_1" true \n' +
                '    right \n' +
                '        [2] limit 1ll \n' +
                '        [2] seek s19 s25 s26 s20 s21 s22 s23 [s27 = price, s28 = prod] @"04f108c1-b995-43e6-9914-8f9f25adca43" true false \n'
            }
          },
          rejectedPlans: []
        },
        executionStats: {
          executionSuccess: true,
          nReturned: 9,
          executionTimeMillis: 1,
          totalKeysExamined: 55,
          totalDocsExamined: 34,
          executionStages: {
            stage: 'project',
            planNodeId: 4,
            nReturned: 9,
            executionTimeMillisEstimate: 0,
            opens: 1,
            closes: 1,
            saveState: 1,
            restoreState: 1,
            isEOF: 1,
            projections: { '34': 'newObj("_id", s32, "totalSum", s33) ' },
            inputStage: {
              stage: 'project',
              planNodeId: 4,
              nReturned: 9,
              executionTimeMillisEstimate: 0,
              opens: 1,
              closes: 1,
              saveState: 1,
              restoreState: 1,
              isEOF: 1,
              projections: {
                '32': 'newObj("prod", s29) ',
                '33': 'doubleDoubleSumFinalize(s30) '
              },
              inputStage: {
                stage: 'group',
                planNodeId: 4,
                nReturned: 9,
                executionTimeMillisEstimate: 0,
                opens: 1,
                closes: 1,
                saveState: 1,
                restoreState: 1,
                isEOF: 1,
                groupBySlots: [ Long('29') ],
                expressions: {
                  '30': 'aggDoubleDoubleSum(s27) ',
                  initExprs: { '30': null }
                },
                mergingExprs: { '31': 'aggMergeDoubleDoubleSums(s31) ' },
                usedDisk: false,
                spills: 0,
                spilledBytes: 0,
                spilledRecords: 0,
                spilledDataStorageSize: 0,
                inputStage: {
                  stage: 'project',
                  planNodeId: 4,
                  nReturned: 34,
                  executionTimeMillisEstimate: 0,
                  opens: 1,
                  closes: 1,
                  saveState: 1,
                  restoreState: 1,
                  isEOF: 1,
                  projections: { '29': '(s28 ?: null) ' },
                  inputStage: {
                    stage: 'nlj',
                    planNodeId: 2,
                    nReturned: 34,
                    executionTimeMillisEstimate: 0,
                    opens: 1,
                    closes: 1,
                    saveState: 1,
                    restoreState: 1,
                    isEOF: 1,
                    totalDocsExamined: 34,
                    totalKeysExamined: 55,
                    collectionScans: 0,
                    collectionSeeks: 34,
                    indexScans: 0,
                    indexSeeks: 1,
                    indexesUsed: [
                      'customer_1_city_1_date_1',
                      'customer_1_city_1_date_1'
                    ],
                    innerOpens: 34,
                    innerCloses: 1,
                    outerProjects: [],
                    outerCorrelated: [
                      Long('19'),
                      Long('20'),
                      Long('21'),
                      Long('22'),
                      Long('23')
                    ],
                    outerStage: {
                      stage: 'branch',
                      planNodeId: 1,
                      nReturned: 34,
                      executionTimeMillisEstimate: 0,
                      opens: 1,
                      closes: 1,
                      saveState: 1,
                      restoreState: 1,
                      isEOF: 1,
                      numTested: 1,
                      thenBranchOpens: 1,
                      thenBranchCloses: 1,
                      elseBranchOpens: 0,
                      elseBranchCloses: 0,
                      filter: 's24 ',
                      thenSlots: [
                        Long('4'),
                        Long('6'),
                        Long('7'),
                        Long('8'),
                        Long('9')
                      ],
                      elseSlots: [
                        Long('10'),
                        Long('16'),
                        Long('17'),
                        Long('18'),
                        Long('9')
                      ],
                      outputSlots: [
                        Long('19'),
                        Long('20'),
                        Long('21'),
                        Long('22'),
                        Long('23')
                      ],
                      thenStage: {
                        stage: 'ixscan_generic',
                        planNodeId: 1,
                        nReturned: 34,
                        executionTimeMillisEstimate: 0,
                        opens: 1,
                        closes: 1,
                        saveState: 1,
                        restoreState: 1,
                        isEOF: 1,
                        indexName: 'customer_1_city_1_date_1',
                        keysExamined: 55,
                        seeks: 21,
                        numReads: 55,
                        indexKeySlot: 8,
                        recordIdSlot: 4,
                        snapshotIdSlot: 6,
                        indexIdentSlot: 7,
                        outputSlots: [],
                        indexKeysToInclude: '00000000000000000000000000000000'
                      },
                      elseStage: {
                        stage: 'nlj',
                        planNodeId: 1,
                        nReturned: 0,
                        executionTimeMillisEstimate: 0,
                        opens: 0,
                        closes: 0,
                        saveState: 1,
                        restoreState: 1,
                        isEOF: 0,
                        totalDocsExamined: 0,
                        totalKeysExamined: 0,
                        collectionScans: 0,
                        collectionSeeks: 0,
                        indexScans: 0,
                        indexSeeks: 0,
                        indexesUsed: [ 'customer_1_city_1_date_1' ],
                        innerOpens: 0,
                        innerCloses: 0,
                        outerProjects: [],
                        outerCorrelated: [ Long('11'), Long('12') ],
                        outerStage: {
                          stage: 'project',
                          planNodeId: 1,
                          nReturned: 0,
                          executionTimeMillisEstimate: 0,
                          opens: 0,
                          closes: 0,
                          saveState: 1,
                          restoreState: 1,
                          isEOF: 0,
                          projections: {
                            '11': 'getField(s14, "l") ',
                            '12': 'getField(s14, "h") '
                          },
                          inputStage: {
                            stage: 'unwind',
                            planNodeId: 1,
                            nReturned: 0,
                            executionTimeMillisEstimate: 0,
                            opens: 0,
                            closes: 0,
                            saveState: 1,
                            restoreState: 1,
                            isEOF: 0,
                            inputSlot: 13,
                            outSlot: 14,
                            outIndexSlot: 15,
                            preserveNullAndEmptyArrays: 0,
                            inputStage: {
                              stage: 'limit',
                              planNodeId: 1,
                              nReturned: 0,
                              executionTimeMillisEstimate: 0,
                              opens: 0,
                              closes: 0,
                              saveState: 1,
                              restoreState: 1,
                              isEOF: 0,
                              inputStage: {
                                stage: 'coscan',
                                planNodeId: 1,
                                nReturned: 0,
                                executionTimeMillisEstimate: 0,
                                opens: 0,
                                closes: 0,
                                saveState: 1,
                                restoreState: 1,
                                isEOF: 0
                              }
                            }
                          }
                        },
                        innerStage: {
                          stage: 'ixseek',
                          planNodeId: 1,
                          nReturned: 0,
                          executionTimeMillisEstimate: 0,
                          opens: 0,
                          closes: 0,
                          saveState: 1,
                          restoreState: 1,
                          isEOF: 0,
                          indexName: 'customer_1_city_1_date_1',
                          keysExamined: 0,
                          seeks: 0,
                          numReads: 0,
                          indexKeySlot: 18,
                          recordIdSlot: 10,
                          snapshotIdSlot: 16,
                          indexIdentSlot: 17,
                          outputSlots: [],
                          indexKeysToInclude: '00000000000000000000000000000000',
                          seekKeyLow: 's11 ',
                          seekKeyHigh: 's12 '
                        }
                      }
                    },
                    innerStage: {
                      stage: 'limit',
                      planNodeId: 2,
                      nReturned: 34,
                      executionTimeMillisEstimate: 0,
                      opens: 34,
                      closes: 1,
                      saveState: 1,
                      restoreState: 1,
                      isEOF: 1,
                      limit: 1,
                      inputStage: {
                        stage: 'seek',
                        planNodeId: 2,
                        nReturned: 34,
                        executionTimeMillisEstimate: 0,
                        opens: 34,
                        closes: 1,
                        saveState: 1,
                        restoreState: 1,
                        isEOF: 0,
                        numReads: 34,
                        recordSlot: 25,
                        recordIdSlot: 26,
                        seekKeySlot: 19,
                        snapshotIdSlot: 20,
                        indexIdentSlot: 21,
                        indexKeySlot: 22,
                        indexKeyPatternSlot: 23,
                        fields: [ 'price', 'prod' ],
                        outputSlots: [ Long('27'), Long('28') ]
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      nReturned: Long('9'),
      executionTimeMillisEstimate: Long('0')
    },
    {
      '$sort': { sortKey: { _id: 1 } },
      totalDataSizeSortedBytesEstimate: Long('6687'),
      usedDisk: false,
      spills: Long('0'),
      spilledDataStorageSize: Long('0'),
      nReturned: Long('9'),
      executionTimeMillisEstimate: Long('0')
    }
  ],
  serverInfo: {
    host: 'rhel8',
    port: 27017,
    version: '7.0.16',
    gitVersion: '18b949444cfdaa88e30b0e10243bc18268251c1f'
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
  command: {
    aggregate: 'orders',
    pipeline: [
      {
        '$match': {
          '$and': [
            { customer: 'Ivan' },
            { date: { '$gte': '2023-10-08 09:00:00' } },
            { date: { '$lt': '2023-10-08 15:00:00' } }
          ]
        }
      },
      {
        '$group': { _id: { prod: '$prod' }, totalSum: { '$sum': '$price' } }
      },
      { '$sort': { _id: 1 } }
    ],
    cursor: {},
    '$db': 'test'
  },
  ok: 1
}
```

Выполняю запрос в ArangoDB:
```
127.0.0.1:8529@test> db._query('FOR doc IN orders FILTER doc.date >= "2023-10-08 09:00:00" AND doc.date < "2023-10-08 15:00:00" AND doc.customer == "Ivan" COLLECT prod = doc.prod AGGREGATE sum = sum(doc.price) SORT prod RETURN { prod, sum }').toArray()
[
  {
    "prod" : "AutoGoods",
    "sum" : 1374
  },
  {
    "prod" : "Books",
    "sum" : 2325
  },
  {
    "prod" : "Cloth",
    "sum" : 2644
  },
  {
    "prod" : "Drinks",
    "sum" : 983
  },
  {
    "prod" : "Foods",
    "sum" : 3464
  },
  {
    "prod" : "Hobby",
    "sum" : 2345
  },
  {
    "prod" : "Hosehold",
    "sum" : 492
  },
  {
    "prod" : "Pharmacy",
    "sum" : 3540
  },
  {
    "prod" : "Shoes",
    "sum" : 3182
  }
]
```
```
127.0.0.1:8529@test> db._query('FOR doc IN orders FILTER doc.date >= "2023-10-08 09:00:00" AND doc.date < "2023-10-08 15:00:00" AND doc.customer == "Ivan" COLLECT prod = doc.prod AGGREGATE sum = sum(doc.price) SORT prod RETURN { prod, sum }').getExtra()
{
  "warnings" : [ ],
  "stats" : {
    "writesExecuted" : 0,
    "writesIgnored" : 0,
    "documentLookups" : 34,
    "seeks" : 0,
    "scannedFull" : 0,
    "scannedIndex" : 100045,
    "cursorsCreated" : 1,
    "cursorsRearmed" : 0,
    "cacheHits" : 0,
    "cacheMisses" : 0,
    "filtered" : 100010,
    "httpRequests" : 0,
    "executionTime" : 0.04769805199975963,
    "peakMemoryUsage" : 65536,
    "intermediateCommits" : 0
  }
}
```

__РЕЗУЛЬТАТ__: в MongoDB запрос выполнился за 1 мс, а в ArangoDB за 48 мс.

Попробую построить в ArangoDB более подходящий индекс:
```
127.0.0.1:8529@test> db.orders.ensureIndex({ type: "persistent", fields: [ "customer", "date", "prod" ] });
{
  "cacheEnabled" : false,
  "deduplicate" : true,
  "estimates" : true,
  "fields" : [
    "customer",
    "date",
    "prod"
  ],
  "id" : "orders/11139292",
  "isNewlyCreated" : true,
  "name" : "idx_1823935444574797824",
  "selectivityEstimate" : 0.9998779445868424,
  "sparse" : false,
  "type" : "persistent",
  "unique" : false,
  "code" : 201
}
```

Выполняю запрос в ArangoDB ещё раз:
```
127.0.0.1:8529@test> db._query('FOR doc IN orders FILTER doc.date >= "2023-10-08 09:00:00" AND doc.date < "2023-10-08 15:00:00" AND doc.customer == "Ivan" COLLECT prod = doc.prod AGGREGATE sum = sum(doc.price) SORT prod RETURN { prod, sum }').getExtra()
{
  "warnings" : [ ],
  "stats" : {
    "writesExecuted" : 0,
    "writesIgnored" : 0,
    "documentLookups" : 34,
    "seeks" : 0,
    "scannedFull" : 0,
    "scannedIndex" : 34,
    "cursorsCreated" : 1,
    "cursorsRearmed" : 0,
    "cacheHits" : 0,
    "cacheMisses" : 0,
    "filtered" : 0,
    "httpRequests" : 0,
    "executionTime" : 0.0006361129999277182,
    "peakMemoryUsage" : 65536,
    "intermediateCommits" : 0
  }
}
```

__РЕЗУЛЬТАТ__: теперь запрос в обеих БД выполняется примерно за 1 мс.

## Выводы

