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
  * Создаю для сервиса файл /etc/systemd/system/disable-transparent-huge-pages.service с содержимым:
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
  * Включаю автозапуск и заупускаю сервиса disable-transparent-huge-pages командами:
    ```
    systemctl enable disable-transparent-huge-pages
    systemctl start disable-transparent-huge-pages
    ```
