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
3. СУБД будут тестироваться в некластерной конфигурации.

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
