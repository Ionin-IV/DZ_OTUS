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
1. Создаю нижеследующий скрипт (bash linux), генерирующий данные в json-файл(ы) для загрузки в БД:
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
2.
