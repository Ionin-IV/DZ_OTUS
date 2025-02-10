# Проектная работа по теме: "Сравнение СУБД ArangoDB, как графовой, с neo4j, и как документоориентированной, с MongoDB"

## Цели проектной работы:

1. Провести фунциональное и нагрузочное тестирование/сравнение СУБД ArangoDB, как графовой, и neo4j.
2. Провести фунциональное и нагрузочное тестирование/сравнение СУБД ArangoDB, как документоориентированной, и MongoDB.

## Стенд для тестирования

1. СУБД будут тестироваться на одной и той же ВМ со следующей спецификацией:
- процессор: 8 ядер
- ОЗУ: 8Гб
- жёсткий диск: 50Гб
- ОС: CentOS 8.5.2111
2. СУБД будут тестироваться в некластерной конфигурации.

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

## Сравнение СУБД ArangoDB, как графовой, с neo4j

### Загрузка тестовых данных в ArangoDB

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
[root@host ~]# arangoimport --file "customers.json" --type json --collection "customers" --server.database "test"
Please specify a password:
2025-01-31T09:54:08.195878Z [6193-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             customers
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        customers.json
file type:              json
threads:                4
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
[root@host ~]# arangoimport --file "shops.json" --type json --collection "shops" --server.database "test"
Please specify a password:
2025-01-31T09:54:22.115856Z [6200-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             shops
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        shops.json
file type:              json
threads:                4
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
[root@host ~]# arangoimport --file "cities.json" --type json --collection "cities" --server.database "test"
Please specify a password:
2025-01-31T09:54:32.283785Z [6207-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             cities
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        cities.json
file type:              json
threads:                4
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
[root@host ~]# arangoimport --file "prods.json" --type json --collection "prods" --server.database "test"
Please specify a password:
2025-01-31T09:54:43.763807Z [6214-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             prods
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        prods.json
file type:              json
threads:                4
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
[root@host ~]# arangoimport --file "orders.json" --type json --collection "orders" --server.database "test"
Please specify a password:
2025-01-31T09:54:54.203794Z [6221-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             orders
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        orders.json
file type:              json
threads:                4
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...
2025-01-31T09:54:54.206563Z [6221-1] INFO [9ddf3] {general} processed 3.1 MB (3%) of input file
2025-01-31T09:54:54.207247Z [6221-1] INFO [9ddf3] {general} processed 5.2 MB (6%) of input file
2025-01-31T09:54:54.209623Z [6221-1] INFO [9ddf3] {general} processed 8.3 MB (9%) of input file
2025-01-31T09:54:54.216689Z [6221-1] INFO [9ddf3] {general} processed 10.4 MB (12%) of input file
2025-01-31T09:54:54.217383Z [6221-1] INFO [9ddf3] {general} processed 13.6 MB (15%) of input file
2025-01-31T09:54:54.217785Z [6221-1] INFO [9ddf3] {general} processed 15.7 MB (18%) of input file
2025-01-31T09:54:54.223664Z [6221-1] INFO [9ddf3] {general} processed 18.8 MB (21%) of input file
2025-01-31T09:54:54.224393Z [6221-1] INFO [9ddf3] {general} processed 22.0 MB (25%) of input file
2025-01-31T09:54:54.224836Z [6221-1] INFO [9ddf3] {general} processed 24.1 MB (28%) of input file
2025-01-31T09:54:54.230579Z [6221-1] INFO [9ddf3] {general} processed 27.2 MB (31%) of input file
2025-01-31T09:54:54.231054Z [6221-1] INFO [9ddf3] {general} processed 29.3 MB (34%) of input file
2025-01-31T09:54:54.231881Z [6221-1] INFO [9ddf3] {general} processed 32.5 MB (37%) of input file
2025-01-31T09:54:54.232381Z [6221-1] INFO [9ddf3] {general} processed 34.6 MB (40%) of input file
2025-01-31T09:54:54.238531Z [6221-1] INFO [9ddf3] {general} processed 37.7 MB (43%) of input file
2025-01-31T09:54:54.239398Z [6221-1] INFO [9ddf3] {general} processed 40.8 MB (47%) of input file
2025-01-31T09:54:54.239955Z [6221-1] INFO [9ddf3] {general} processed 42.9 MB (50%) of input file
2025-01-31T09:54:55.097349Z [6221-1] INFO [9ddf3] {general} processed 46.1 MB (53%) of input file
2025-01-31T09:54:55.097805Z [6221-1] INFO [9ddf3] {general} processed 48.2 MB (56%) of input file
2025-01-31T09:54:55.098680Z [6221-1] INFO [9ddf3] {general} processed 51.3 MB (59%) of input file
2025-01-31T09:54:55.216111Z [6221-1] INFO [9ddf3] {general} processed 53.4 MB (62%) of input file
2025-01-31T09:54:55.217014Z [6221-1] INFO [9ddf3] {general} processed 56.6 MB (65%) of input file
2025-01-31T09:54:55.217927Z [6221-1] INFO [9ddf3] {general} processed 59.7 MB (69%) of input file
2025-01-31T09:54:55.221229Z [6221-1] INFO [9ddf3] {general} processed 61.8 MB (72%) of input file
2025-01-31T09:54:55.222037Z [6221-1] INFO [9ddf3] {general} processed 65.0 MB (75%) of input file
2025-01-31T09:54:55.222474Z [6221-1] INFO [9ddf3] {general} processed 67.1 MB (78%) of input file
2025-01-31T09:54:55.513415Z [6221-1] INFO [9ddf3] {general} processed 70.2 MB (81%) of input file
2025-01-31T09:54:55.513620Z [6221-1] INFO [9ddf3] {general} processed 72.3 MB (84%) of input file
2025-01-31T09:54:55.513892Z [6221-1] INFO [9ddf3] {general} processed 75.4 MB (87%) of input file
2025-01-31T09:54:56.219477Z [6221-1] INFO [9ddf3] {general} processed 78.6 MB (91%) of input file
2025-01-31T09:54:56.219988Z [6221-1] INFO [9ddf3] {general} processed 80.7 MB (94%) of input file
2025-01-31T09:54:56.220659Z [6221-1] INFO [9ddf3] {general} processed 83.8 MB (97%) of input file
2025-01-31T09:54:56.220944Z [6221-1] INFO [9ddf3] {general} processed 85.7 MB (100%) of input file

created:          1000000
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@host ~]# arangoimport --file "customer_to_order.json" --type json --collection "customer_to_order" --server.database "test"
Please specify a password:
2025-01-31T09:55:15.339888Z [6619-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             customer_to_order
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        customer_to_order.json
file type:              json
threads:                4
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...
2025-01-31T09:55:15.341899Z [6619-1] INFO [9ddf3] {general} processed 2.0 MB (3%) of input file
2025-01-31T09:55:15.343311Z [6619-1] INFO [9ddf3] {general} processed 4.1 MB (6%) of input file
2025-01-31T09:55:15.345692Z [6619-1] INFO [9ddf3] {general} processed 6.2 MB (10%) of input file
2025-01-31T09:55:15.346481Z [6619-1] INFO [9ddf3] {general} processed 8.3 MB (14%) of input file
2025-01-31T09:55:15.353867Z [6619-1] INFO [9ddf3] {general} processed 10.4 MB (17%) of input file
2025-01-31T09:55:15.356303Z [6619-1] INFO [9ddf3] {general} processed 12.5 MB (21%) of input file
2025-01-31T09:55:15.356805Z [6619-1] INFO [9ddf3] {general} processed 14.6 MB (25%) of input file
2025-01-31T09:55:15.357181Z [6619-1] INFO [9ddf3] {general} processed 16.7 MB (28%) of input file
2025-01-31T09:55:15.363408Z [6619-1] INFO [9ddf3] {general} processed 18.8 MB (32%) of input file
2025-01-31T09:55:15.363896Z [6619-1] INFO [9ddf3] {general} processed 20.9 MB (36%) of input file
2025-01-31T09:55:15.364390Z [6619-1] INFO [9ddf3] {general} processed 23.0 MB (40%) of input file
2025-01-31T09:55:15.364861Z [6619-1] INFO [9ddf3] {general} processed 25.1 MB (43%) of input file
2025-01-31T09:55:15.370259Z [6619-1] INFO [9ddf3] {general} processed 27.2 MB (47%) of input file
2025-01-31T09:55:15.370702Z [6619-1] INFO [9ddf3] {general} processed 29.3 MB (51%) of input file
2025-01-31T09:55:15.371144Z [6619-1] INFO [9ddf3] {general} processed 31.4 MB (54%) of input file
2025-01-31T09:55:15.371660Z [6619-1] INFO [9ddf3] {general} processed 33.5 MB (58%) of input file
2025-01-31T09:55:15.376515Z [6619-1] INFO [9ddf3] {general} processed 35.6 MB (62%) of input file
2025-01-31T09:55:15.376934Z [6619-1] INFO [9ddf3] {general} processed 37.7 MB (66%) of input file
2025-01-31T09:55:15.377373Z [6619-1] INFO [9ddf3] {general} processed 39.8 MB (69%) of input file
2025-01-31T09:55:15.377799Z [6619-1] INFO [9ddf3] {general} processed 41.9 MB (73%) of input file
2025-01-31T09:55:18.453164Z [6619-1] INFO [9ddf3] {general} processed 44.0 MB (77%) of input file
2025-01-31T09:55:18.453625Z [6619-1] INFO [9ddf3] {general} processed 46.1 MB (80%) of input file
2025-01-31T09:55:18.454057Z [6619-1] INFO [9ddf3] {general} processed 48.2 MB (84%) of input file
2025-01-31T09:55:18.454454Z [6619-1] INFO [9ddf3] {general} processed 50.3 MB (88%) of input file
2025-01-31T09:55:18.454778Z [6619-1] INFO [9ddf3] {general} processed 52.4 MB (92%) of input file
2025-01-31T09:55:18.783241Z [6619-1] INFO [9ddf3] {general} processed 54.5 MB (95%) of input file
2025-01-31T09:55:18.783858Z [6619-1] INFO [9ddf3] {general} processed 56.4 MB (99%) of input file

created:          1000000
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@host ~]# arangoimport --file "order_to_city.json" --type json --collection "order_to_city" --server.database "test"
Please specify a password:
2025-01-31T09:55:35.283892Z [6632-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             order_to_city
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        order_to_city.json
file type:              json
threads:                4
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...
2025-01-31T09:55:35.286172Z [6632-1] INFO [9ddf3] {general} processed 2.0 MB (3%) of input file
2025-01-31T09:55:35.287637Z [6632-1] INFO [9ddf3] {general} processed 4.1 MB (6%) of input file
2025-01-31T09:55:35.290014Z [6632-1] INFO [9ddf3] {general} processed 6.2 MB (10%) of input file
2025-01-31T09:55:35.290792Z [6632-1] INFO [9ddf3] {general} processed 8.3 MB (14%) of input file
2025-01-31T09:55:35.298896Z [6632-1] INFO [9ddf3] {general} processed 10.4 MB (18%) of input file
2025-01-31T09:55:35.299319Z [6632-1] INFO [9ddf3] {general} processed 12.5 MB (22%) of input file
2025-01-31T09:55:35.299821Z [6632-1] INFO [9ddf3] {general} processed 14.6 MB (26%) of input file
2025-01-31T09:55:35.300210Z [6632-1] INFO [9ddf3] {general} processed 16.7 MB (29%) of input file
2025-01-31T09:55:35.305802Z [6632-1] INFO [9ddf3] {general} processed 18.8 MB (33%) of input file
2025-01-31T09:55:35.306437Z [6632-1] INFO [9ddf3] {general} processed 20.9 MB (37%) of input file
2025-01-31T09:55:35.306911Z [6632-1] INFO [9ddf3] {general} processed 23.0 MB (41%) of input file
2025-01-31T09:55:35.307469Z [6632-1] INFO [9ddf3] {general} processed 25.1 MB (45%) of input file
2025-01-31T09:55:35.313601Z [6632-1] INFO [9ddf3] {general} processed 27.2 MB (49%) of input file
2025-01-31T09:55:35.314041Z [6632-1] INFO [9ddf3] {general} processed 29.3 MB (53%) of input file
2025-01-31T09:55:35.314456Z [6632-1] INFO [9ddf3] {general} processed 31.4 MB (56%) of input file
2025-01-31T09:55:35.314883Z [6632-1] INFO [9ddf3] {general} processed 33.5 MB (60%) of input file
2025-01-31T09:55:35.319564Z [6632-1] INFO [9ddf3] {general} processed 35.6 MB (64%) of input file
2025-01-31T09:55:35.319990Z [6632-1] INFO [9ddf3] {general} processed 37.7 MB (68%) of input file
2025-01-31T09:55:35.320388Z [6632-1] INFO [9ddf3] {general} processed 39.8 MB (72%) of input file
2025-01-31T09:55:35.320776Z [6632-1] INFO [9ddf3] {general} processed 41.9 MB (76%) of input file
2025-01-31T09:55:38.563977Z [6632-1] INFO [9ddf3] {general} processed 44.0 MB (79%) of input file
2025-01-31T09:55:38.564550Z [6632-1] INFO [9ddf3] {general} processed 46.1 MB (83%) of input file
2025-01-31T09:55:38.564972Z [6632-1] INFO [9ddf3] {general} processed 48.2 MB (87%) of input file
2025-01-31T09:55:38.565395Z [6632-1] INFO [9ddf3] {general} processed 50.3 MB (91%) of input file
2025-01-31T09:55:38.915210Z [6632-1] INFO [9ddf3] {general} processed 52.4 MB (95%) of input file
2025-01-31T09:55:38.915683Z [6632-1] INFO [9ddf3] {general} processed 54.4 MB (99%) of input file

created:          1000000
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@host ~]# arangoimport --file "order_to_prods.json" --type json --collection "order_to_prods" --server.database "test"
Please specify a password:
2025-01-31T09:56:01.459897Z [6649-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             order_to_prods
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        order_to_prods.json
file type:              json
threads:                4
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...
2025-01-31T09:56:01.461753Z [6649-1] INFO [9ddf3] {general} processed 2.0 MB (3%) of input file
2025-01-31T09:56:01.463085Z [6649-1] INFO [9ddf3] {general} processed 4.1 MB (6%) of input file
2025-01-31T09:56:01.465312Z [6649-1] INFO [9ddf3] {general} processed 6.2 MB (10%) of input file
2025-01-31T09:56:01.466001Z [6649-1] INFO [9ddf3] {general} processed 8.3 MB (14%) of input file
2025-01-31T09:56:01.473663Z [6649-1] INFO [9ddf3] {general} processed 10.4 MB (18%) of input file
2025-01-31T09:56:01.474160Z [6649-1] INFO [9ddf3] {general} processed 12.5 MB (22%) of input file
2025-01-31T09:56:01.474599Z [6649-1] INFO [9ddf3] {general} processed 14.6 MB (26%) of input file
2025-01-31T09:56:01.475005Z [6649-1] INFO [9ddf3] {general} processed 16.7 MB (30%) of input file
2025-01-31T09:56:01.475428Z [6649-1] INFO [9ddf3] {general} processed 18.8 MB (34%) of input file
2025-01-31T09:56:01.481374Z [6649-1] INFO [9ddf3] {general} processed 20.9 MB (38%) of input file
2025-01-31T09:56:01.481888Z [6649-1] INFO [9ddf3] {general} processed 23.0 MB (42%) of input file
2025-01-31T09:56:01.482361Z [6649-1] INFO [9ddf3] {general} processed 25.1 MB (46%) of input file
2025-01-31T09:56:01.482823Z [6649-1] INFO [9ddf3] {general} processed 27.2 MB (50%) of input file
2025-01-31T09:56:01.488848Z [6649-1] INFO [9ddf3] {general} processed 29.3 MB (53%) of input file
2025-01-31T09:56:01.489338Z [6649-1] INFO [9ddf3] {general} processed 31.4 MB (57%) of input file
2025-01-31T09:56:01.489852Z [6649-1] INFO [9ddf3] {general} processed 33.5 MB (61%) of input file
2025-01-31T09:56:01.490323Z [6649-1] INFO [9ddf3] {general} processed 35.6 MB (65%) of input file
2025-01-31T09:56:01.495606Z [6649-1] INFO [9ddf3] {general} processed 37.7 MB (69%) of input file
2025-01-31T09:56:01.495953Z [6649-1] INFO [9ddf3] {general} processed 39.8 MB (73%) of input file
2025-01-31T09:56:01.496321Z [6649-1] INFO [9ddf3] {general} processed 41.9 MB (77%) of input file
2025-01-31T09:56:01.496708Z [6649-1] INFO [9ddf3] {general} processed 44.0 MB (81%) of input file
2025-01-31T09:56:04.802806Z [6649-1] INFO [9ddf3] {general} processed 46.1 MB (85%) of input file
2025-01-31T09:56:04.803305Z [6649-1] INFO [9ddf3] {general} processed 48.2 MB (89%) of input file
2025-01-31T09:56:04.803747Z [6649-1] INFO [9ddf3] {general} processed 50.3 MB (93%) of input file
2025-01-31T09:56:04.804321Z [6649-1] INFO [9ddf3] {general} processed 52.4 MB (97%) of input file

created:          1000000
warnings/errors:  0
updated/replaced: 0
ignored:          0
```
```
[root@host ~]# arangoimport --file "order_to_shop.json" --type json --collection "order_to_shop" --server.database "test"
Please specify a password:
2025-01-31T09:56:19.555892Z [6665-1] INFO [11111] {general} This executable uses the GNU C library (glibc), which is licensed under the GNU Lesser General Public License (LGPL), see https://www.gnu.org/copyleft/lesser.html and https://www.gnu.org/licenses/gpl.html
Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.12.3 [unknown, ], database: 'test', username: 'root'
----------------------------------------
database:               test
collection:             order_to_shop
overwrite coll. prefix: no
create:                 no
create database:        no
source filename:        order_to_shop.json
file type:              json
threads:                4
on duplicate:           error
connect timeout:        5
request timeout:        1200
----------------------------------------
Starting JSON import...
2025-01-31T09:56:19.557602Z [6665-1] INFO [9ddf3] {general} processed 2.0 MB (3%) of input file
2025-01-31T09:56:19.558946Z [6665-1] INFO [9ddf3] {general} processed 4.1 MB (6%) of input file
2025-01-31T09:56:19.561475Z [6665-1] INFO [9ddf3] {general} processed 6.2 MB (10%) of input file
2025-01-31T09:56:19.562298Z [6665-1] INFO [9ddf3] {general} processed 8.3 MB (14%) of input file
2025-01-31T09:56:19.570581Z [6665-1] INFO [9ddf3] {general} processed 10.4 MB (18%) of input file
2025-01-31T09:56:19.571143Z [6665-1] INFO [9ddf3] {general} processed 12.5 MB (22%) of input file
2025-01-31T09:56:19.571536Z [6665-1] INFO [9ddf3] {general} processed 14.6 MB (26%) of input file
2025-01-31T09:56:19.571898Z [6665-1] INFO [9ddf3] {general} processed 16.7 MB (30%) of input file
2025-01-31T09:56:19.572293Z [6665-1] INFO [9ddf3] {general} processed 18.8 MB (34%) of input file
2025-01-31T09:56:19.578330Z [6665-1] INFO [9ddf3] {general} processed 20.9 MB (38%) of input file
2025-01-31T09:56:19.578714Z [6665-1] INFO [9ddf3] {general} processed 23.0 MB (42%) of input file
2025-01-31T09:56:19.579229Z [6665-1] INFO [9ddf3] {general} processed 25.1 MB (46%) of input file
2025-01-31T09:56:19.579730Z [6665-1] INFO [9ddf3] {general} processed 27.2 MB (50%) of input file
2025-01-31T09:56:19.585500Z [6665-1] INFO [9ddf3] {general} processed 29.3 MB (54%) of input file
2025-01-31T09:56:19.585970Z [6665-1] INFO [9ddf3] {general} processed 31.4 MB (58%) of input file
2025-01-31T09:56:19.586448Z [6665-1] INFO [9ddf3] {general} processed 33.5 MB (62%) of input file
2025-01-31T09:56:19.586891Z [6665-1] INFO [9ddf3] {general} processed 35.6 MB (66%) of input file
2025-01-31T09:56:19.592856Z [6665-1] INFO [9ddf3] {general} processed 37.7 MB (70%) of input file
2025-01-31T09:56:19.593446Z [6665-1] INFO [9ddf3] {general} processed 39.8 MB (74%) of input file
2025-01-31T09:56:19.593930Z [6665-1] INFO [9ddf3] {general} processed 41.9 MB (78%) of input file
2025-01-31T09:56:19.594455Z [6665-1] INFO [9ddf3] {general} processed 44.0 MB (82%) of input file
2025-01-31T09:56:22.950798Z [6665-1] INFO [9ddf3] {general} processed 46.1 MB (86%) of input file
2025-01-31T09:56:22.951267Z [6665-1] INFO [9ddf3] {general} processed 48.2 MB (90%) of input file
2025-01-31T09:56:22.951693Z [6665-1] INFO [9ddf3] {general} processed 50.3 MB (94%) of input file
2025-01-31T09:56:22.952022Z [6665-1] INFO [9ddf3] {general} processed 52.4 MB (98%) of input file

created:          1000000
warnings/errors:  0
updated/replaced: 0
ignored:          0
```

__РЕЗУЛЬТАТ__: 1000000 заказов загружен менне, чем за 20 секунд (исключаяя подготовку данных и сам зпуск команд).

### Загрузка тестовых данных в neo4j

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

### Сравнение команд и их выполнения в ArangoDB и neo4j

