# Домашнее задание по лекции "Elasticsearch"

## Задание

Развернуть Instance ES – желательно в AWS.

Создать в ES индекс, в нём должно быть обязательное поле text типа string.

Создать для индекса pattern.

Добавить в индекс как минимум 3 документа желательно со следующим содержанием:
- «моя мама мыла посуду а кот жевал сосиски»
- «рама была отмыта и вылизана котом»
- «мама мыла раму»

Написать запрос нечеткого поиска к этой коллекции документов ко ключу «мама ела сосиски».

Расшарить коллекцию postman (желательно сдавать в таком формате).

Прислать ссылку на коллекцию.

## Выполнение задания

### Подготовка

1. Создаю ВМ.
2. Скачиваю rpm и устанавливаю Elasticsearch на ВМ.
3. Устанавливаю в браузер Chrome расширение Elasticvue для работы с Elasticsearch.

### Выполнение

1. Создаю индекс otus-lab с mapping-ом (поле content с типом данных text) и поддержкой русского языка:

Команда:
```
PUT /otus-lab
{
    "settings": {
        "analysis": {
            "filter": {
                "ru_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "ru_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "my_russian": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "ru_stop",
                        "ru_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {               
          "content": { "type": "text", "analyzer": "my_russian" }
         }
    }
}
```

Ответ:
```
{
  "acknowledged": true,
  "shards_acknowledged": true,
  "index": "otus-lab"
}
```

2. Добавляю в индекс три документа:

Команда:
```
POST /otus-lab/_doc
{
  "content": "моя мама мыла посуду а кот жевал сосиски"
}
```

Ответ:
```
{
  "_index": "otus-lab",
  "_id": "hKO_aJMBbyFVpe5qYApE",
  "_version": 1,
  "result": "created",
  "_shards": {
    "total": 2,
    "successful": 1,
    "failed": 0
  },
  "_seq_no": 0,
  "_primary_term": 1
}
```

Команда:
```
POST /otus-lab/_doc
{
  "content": "рама была отмыта и вылизана котом"
}
```

Ответ:
```
{
  "_index": "otus-lab",
  "_id": "haO_aJMBbyFVpe5q7Apb",
  "_version": 1,
  "result": "created",
  "_shards": {
    "total": 2,
    "successful": 1,
    "failed": 0
  },
  "_seq_no": 1,
  "_primary_term": 1
}
```

Команда:
```
POST /otus-lab/_doc
{
  "content": "мама мыла раму"
}
```

Ответ:
```
{
  "_index": "otus-lab",
  "_id": "hqPAaJMBbyFVpe5qQAol",
  "_version": 1,
  "result": "created",
  "_shards": {
    "total": 2,
    "successful": 1,
    "failed": 0
  },
  "_seq_no": 2,
  "_primary_term": 1
}
```

3. Проверяю, что все три документа добавились в индекс:

Команда:
```
GET /otus-lab/_search
{
  "query": {
    "match_all": { }
  }
}
```

Ответ:
```
{
  "took": 7,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 3,
      "relation": "eq"
    },
    "max_score": 1,
    "hits": [
      {
        "_index": "otus-lab",
        "_id": "hKO_aJMBbyFVpe5qYApE",
        "_score": 1,
        "_source": {
          "content": "моя мама мыла посуду а кот жевал сосиски"
        }
      },
      {
        "_index": "otus-lab",
        "_id": "haO_aJMBbyFVpe5q7Apb",
        "_score": 1,
        "_source": {
          "content": "рама была отмыта и вылизана котом"
        }
      },
      {
        "_index": "otus-lab",
        "_id": "hqPAaJMBbyFVpe5qQAol",
        "_score": 1,
        "_source": {
          "content": "мама мыла раму"
        }
      }
    ]
  }
}
```

4. Запрашиваю полнотекстовым поиском фразу "мама ела сосиски":

Команда:
```
GET /otus-lab/_search
{
  "query": {
    "match": {
      "content": "мама ела сосиски"
    }
  }
}
```

Ответ:
```
{
  "took": 2,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 2,
      "relation": "eq"
    },
    "max_score": 1.2535897,
    "hits": [
      {
        "_index": "otus-lab",
        "_id": "hKO_aJMBbyFVpe5qYApE",
        "_score": 1.2535897,
        "_source": {
          "content": "моя мама мыла посуду а кот жевал сосиски"
        }
      },
      {
        "_index": "otus-lab",
        "_id": "hqPAaJMBbyFVpe5qQAol",
        "_score": 0.5376842,
        "_source": {
          "content": "мама мыла раму"
        }
      }
    ]
  }
}
```

__Результат:__ найдены все документы, содержащие чёткое совпадение с одним из слов запроса.

5. Запрашиваю нечётким полнотекстовым поиском ту же фразу "мама ела сосиски":

Команда:
```
GET /otus-lab/_search
{
  "query": {
    "match": {
      "content": {
        "query": "мама ела сосиски",
        "fuzziness": "auto"
      }
    }
  }
}
```

Ответ:
```
{
  "took": 7,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 3,
      "relation": "eq"
    },
    "max_score": 1.2535897,
    "hits": [
      {
        "_index": "otus-lab",
        "_id": "hKO_aJMBbyFVpe5qYApE",
        "_score": 1.2535897,
        "_source": {
          "content": "моя мама мыла посуду а кот жевал сосиски"
        }
      },
      {
        "_index": "otus-lab",
        "_id": "hqPAaJMBbyFVpe5qQAol",
        "_score": 0.89614034,
        "_source": {
          "content": "мама мыла раму"
        }
      },
      {
        "_index": "otus-lab",
        "_id": "haO_aJMBbyFVpe5q7Apb",
        "_score": 0.3235163,
        "_source": {
          "content": "рама была отмыта и вылизана котом"
        }
      }
    ]
  }
}
```

__Результат:__ найден ещё один документ, не содержащий слов из запрошенной фразы. Очевидно, что слово "рама" было интерпретировано, как слово "мама" с ошибкой.
