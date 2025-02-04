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

3. Собираю сгенерированные потоками части данных в один json-файл:
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

