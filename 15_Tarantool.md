# Домашнее задание по лекции "Tarantool"

## Задание

1. Установите Tarantool одним из доступных способов: через виртуальную машину (ВМ) или Docker.
2. Создайте в Box спейс (таблицу) для хранения данных о поисках авиабилетов с полями:
- id (уникальный идентификатор),
- airline (авиакомпания),
- departure_date (дата вылета),
- departure_city (город вылета),
- arrival_city (город прилета),
- min_price (минимальная стоимость авиабилета).
3. Добавьте первичный индекс для спейса.
4. Создайте вторичный индекс на поля departure_date, airline и departure_city.
5. Вставьте несколько записей в спейс.
6. Напишите запрос для выборки минимальной стоимости авиабилета на рейсы с датой вылета 01.01.2025.
7. Реализуйте функцию на Lua для вывода списка рейсов с минимальной стоимостью билета менее 3000 рублей.

На проверку отправьте текстовый документ, содержащий:
- текст выполняемых запросов и настроек для каждого этапа задания;
- код функции на Lua;
- скриншоты вывода запросов и результата работы функции.

## Выполнение задания

### Установка и настройка Tarantool

1. Устанавливаю необходимые пакеты:
```
yum install tarantool
yum install tt
```

2. Создаю директорию для Tarantool:
```
mkdir /opt/tarantool
```

3. Инициализирую структуру необходимых директорий и файлов:
```
cd /opt/tarantool
tt init
```

4. Создаю директории для экземпляра СУБД:
```
cd instances.enabled
mkdir create_db
cd create_db
```

5. Создаю конфигурационные файлы экземпляра СУБД:

Файл instances.yml со следующим содержимым:
```
instance001:
```

Файл config.yml со следующим содержимым:
```
groups:
  group001:
    replicasets:
      replicaset001:
        instances:
          instance001:
            iproto:
              listen:
              - uri: '127.0.0.1:3301'
```

6. Запускаю экземпляр СУБД:
```
tt start create_db
```

7. Проверяю, что экземпляр СУБД запустился и работает:
```
# tt status create_db
 INSTANCE               STATUS   PID    MODE  CONFIG  BOX      UPSTREAM
 create_db:instance001  RUNNING  17923  RW    ready   running  --
```

### Создание спейса

1. Захожу в консоль СУБД:
```
tt connect create_db:instance001
```

2. Создаю спейс avia_tickets:
```
create_db:instance001> box.schema.space.create('avia_tickets')
---
- is_local: false
  engine: memtx
  before_replace: 'function: 0x7f1d54814808'
  field_count: 0
  is_sync: false
  on_replace: 'function: 0x7f1d536936d0'
  state:
    is_sync: false
  temporary: false
  index: []
  type: normal
  enabled: false
  name: avia_tickets
  id: 512
- created
...
```

3. Задаю формат данных в созданном спейсе:
```
create_db:instance001> box.space.avia_tickets:format({
    {name = 'id', type = 'unsigned'},
    {name = 'airline', type = 'string'},
    {name = 'departure_date', type = 'string'},
    {name = 'departure_city', type = 'string'},
    {name = 'arrival_city', type = 'string'},
    {name = 'min_price', type = 'unsigned'}
})
---
...
```

4. Создаю первичный индекс по полю id:
```
create_db:instance001> box.space.avia_tickets:create_index('primary', { parts = { 'id' } })
---
- unique: true
  parts:
  - fieldno: 1
    sort_order: asc
    type: unsigned
    exclude_null: false
    is_nullable: false
  hint: true
  id: 0
  type: TREE
  space_id: 512
  name: primary
...
```

5. Создаю вторичный индекс по полям departure_date, airline, departure_city:
```
create_db:instance001> box.space.avia_tickets:create_index('secondary', {parts = {'departure_date','airline','departure_city'}})
---
- unique: true
  parts:
  - fieldno: 3
    sort_order: asc
    type: string
    exclude_null: false
    is_nullable: false
  - fieldno: 2
    sort_order: asc
    type: string
    exclude_null: false
    is_nullable: false
  - fieldno: 4
    sort_order: asc
    type: string
    exclude_null: false
    is_nullable: false
  hint: true
  id: 1
  type: TREE
  space_id: 512
  name: secondary
 ...
```

6. Заполняю спейс данными о рейсах:
```
box.space.avia_tickets:insert{1, 'Aeroflot', '2024-12-31', 'Moscow', 'Saint Petersburg', 1500}
box.space.avia_tickets:insert{2, 'S7', '2024-12-31', 'Kazan', 'Omsk', 3000}
box.space.avia_tickets:insert{3, 'UTair', '2024-12-31', 'Vladivostok', 'Izhevsk', 5000}
box.space.avia_tickets:insert{4, 'Ural Airlines', '2024-12-31', 'Vladikavkaz', 'Voronezh', 3500}
box.space.avia_tickets:insert{5, 'Rossiya', '2025-01-01', 'Barnaul', 'Kaliningrad', 4000}
box.space.avia_tickets:insert{6, 'Pobeda', '2025-01-01', 'Magnitogorsk', 'Khabarovsk', 2500}
box.space.avia_tickets:insert{7, 'RedWings', '2025-01-01', 'Apatity', 'Ekaterinburg', 4000}
box.space.avia_tickets:insert{8, 'NordStar', '2025-01-01', 'Izhevsk', 'Volgograd', 3500}
box.space.avia_tickets:insert{9, 'Yakutia', '2025-01-02', 'Magadan', 'Magnitogorsk', 3000}
box.space.avia_tickets:insert{10, 'Aurora', '2025-01-02', 'Nalchik', 'Tomsk', 4000}
box.space.avia_tickets:insert{11, 'Gazprom Avia', '2025-01-02', 'Petrozavodsk', 'Samara', 2000}
box.space.avia_tickets:insert{12, 'NordAvia', '2025-01-02', 'Stavropol', 'Ulan-Ude', 3500}
```

### Запрос

1. Для выполнения запроса, создаю ещё один вторичный не уникальный индекс по полям departure_date, min_price:
```
create_db:instance001> box.space.avia_tickets:create_index('secondary2', {parts = {'departure_date', 'min_price'}, unique = false})
---
- unique: false
  parts:
  - fieldno: 3
    sort_order: asc
    type: string
    exclude_null: false
    is_nullable: false
  - fieldno: 6
    sort_order: asc
    type: unsigned
    exclude_null: false
    is_nullable: false
  hint: true
  id: 2
  type: TREE
  space_id: 512
  name: secondary2
...
```

2. Выполняю запрос для выборки минимальной стоимости авиабилета на рейсы с датой вылета 01.01.2025:
```
create_db:instance001> box.space.avia_tickets.index.secondary2:min('2025-01-01')
---
- [6, 'Pobeda', '2025-01-01', 'Magnitogorsk', 'Khabarovsk', 2500]
...
```

### Функция на Lua

Создаю функцию, выводящую список рейсов с минимальной стоимостью билета меньше 3000:
```
create_db:instance001> function less_3000()
for _, tuple in box.space.avia_tickets.index.secondary2:pairs() do
             if (tuple[6] < 3000) then box.session.push(tuple) end
end
end
---
...
```

Запускаю созданную функцию и получаю результат:
```
create_db:instance001> function less_3000()
- 1
- Aeroflot
- "2024-12-31"
- Moscow
- Saint Petersburg
- 1500

- 6
- Pobeda
- "2025-01-01"
- Magnitogorsk
- Khabarovsk
- 2500

- 11
- Gazprom Avia
- "2025-01-02"
- Petrozavodsk
- Samara
- 2000

---
...
```

__ПРИМЕЧАНИЕ:__ для вывода полученныйх значений, пришлось применить функцию box.session.push(), потому что:
- функция print() выводит результаты не в консоль tt, а в stdout ( https://github.com/tarantool/tarantool/issues/1986 );
- return в цикле выводит только первое значение.
