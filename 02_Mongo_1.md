# Домашнее задание по лекции "Базовые возможности MongoDB"

## Задание

Необходимо:
- установить MongoDB одним из способов: ВМ, докер;
- заполнить данными;
- написать несколько запросов на выборку и обновление данных

Задание повышенной сложности*:
- создать индексы и сравнить производительность.

## Ответ:

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
