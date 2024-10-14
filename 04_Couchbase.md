# Домашнее задание по лекции "Couchbase"

## Задание

Необходимо:
- Развернуть кластер Couchbase.
- Создать БД, наполнить небольшими тестовыми данными.
- Проверить отказоустойчивость.

## Выполнение задания:

### Установка MongoDB:

1. Создаю три ВМ в конфигурации: 2 ядра процессора, 2 Гб памяти, 15 Гб жесткий диск, ОС CentOS 7.9

2. Устанавливаю JRE.

3. Подключаю репозиторий Couchbase:
```
curl -O https://packages.couchbase.com/releases/couchbase-release/couchbase-release-1.0.noarch.rpm
yum install ./couchbase-release-1.0.noarch.rpm
```

4. Устанавливаю Couchbase:
```
yum install couchbase-server-community
```

### Создание кластера

1. Захожу на первый сервер по адресу http://192.168.1.21:8091

2. Нажимаю "Setup New Cluster":

![alt text](./04_Couchbase/01.jpg)

3. Ввожу имя кластера, пользователя и его пароль:

![alt text](./04_Couchbase/02.jpg)

4. Соглашаюсь с пользовательским соглашением и нажимаю "Configure Disk, Memory, Services":

![alt text](./04_Couchbase/03.jpg)

5. Ввожу только IP-адрес первого сревера (остальные параметры оставляю по умолчанию) и нажимаю "Save & Finish":

![alt text](./04_Couchbase/04.jpg)

6. В списке серверов появляется первый сервер. Добавляю следующий сервер, нажав "Add Server":

![alt text](./04_Couchbase/05.jpg)

7. Ввожу IP-адрес второго сервера и логин/пароль ранее созданного администратора, и нажимаю "Add Server":

![alt text](./04_Couchbase/06.jpg)

8. Второй сервер добавлен, но требуется перебалнисровка, для чего нажимаю "Rebalance":

![alt text](./04_Couchbase/07.jpg)

9. Новый сервер добавлен и готов к работе:

![alt text](./04_Couchbase/08.jpg)

10. Таким же образом добавляю третий сервер и ребалансирую кластер. Кластер готов к работе:

![alt text](./04_Couchbase/10.jpg)

### Создание Bucket, Scope и Collection

1. Перехожу в закладку "Buckets" и нажимаю "Add Bucket":

![alt text](./04_Couchbase/11.jpg)

2. Ввожу имя test, выбираю количество реплик 2 (остальные параметры оставляю по умолчанию), и нажимаю "Add Bucket":

![alt text](./04_Couchbase/12.jpg)

3. Bucket test создан. Нажимаю в нём "Scopes & Collections":

![alt text](./04_Couchbase/15.jpg)

4. Создаю scope, нажав "Add Scope":

![alt text](./04_Couchbase/16.jpg)

5. Выбираю bucket, ввожу название scope, и создаю его, нажав "Save":

![alt text](./04_Couchbase/17.jpg)

6. Новый scope создан. Нажимаю "Add Collection" в нём:

![alt text](./04_Couchbase/18.jpg)

7. Задаю имя коллекции и нажимаю "Save":

![alt text](./04_Couchbase/19.jpg)

8. Коллекция operation добавлена:

![alt text](./04_Couchbase/20.jpg)

