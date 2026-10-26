# Лабораторная работа №2. Знакомство с Docker

## Описание работы

В рамках лабораторной работы выполняется контейнеризация учебного FastAPI-приложения Personal Assistant. Рассматриваются создание Docker-образа, запуск контейнера, оптимизация сборки, настройка `.dockerignore`, проверка состояния сервиса и тегирование образов.

Работа выполнена с использованием Docker Desktop и Ubuntu (WSL).

## 1. Структура проекта

```text
docker-lab2/
├── app/
│   └── main.py
├── requirements.txt
├── Dockerfile
├── Dockerfile.optimized
├── .dockerignore
└── README.md
```

Основные файлы проекта:

- `app/main.py` — исходный код FastAPI-приложения.
- `requirements.txt` — зависимости Python.
- `Dockerfile` — базовая конфигурация образа.
- `Dockerfile.optimized` — оптимизированная конфигурация с Healthcheck.
- `.dockerignore` — исключения из контекста сборки.
- `README.md` — инструкция по воспроизведению работы.

## 2. Подготовка окружения

Для выполнения работы необходим установленный и запущенный Docker.

Проверка доступности Docker:

```bash
docker version
docker info
```

Для получения исходных файлов приложения используется репозиторий:

```bash
git clone https://github.com/grettl/docker-lab2.git
cd docker-lab2
```

## 3. Создание и запуск базового образа

Базовый образ создаётся на основе `python:3.11-slim`. В Dockerfile указаны рабочая директория, зависимости, исходный код приложения и команда запуска Uvicorn.

Сборка первой версии:

```bash
docker build -t rekun-assistant:v1 .
```

Запуск контейнера:

```bash
docker run -d \
  --name rekun-assistant-1 \
  -p 5458:5458 \
  -e APP_OWNER=rekun \
  -e APP_SECRET=your_secret_key \
  rekun-assistant:v1
```

Значение `APP_SECRET` в приведённой команде является примером и может быть заменено собственным ключом.

Проверка запущенного контейнера:

```bash
docker ps
docker port rekun-assistant-1
```

Приложение доступно по адресу `http://localhost:5458/`.

## 4. Проверка работы приложения

Основные маршруты API:

| Метод | Маршрут | Назначение |
|---|---|---|
| GET | `/` | Главная страница |
| GET | `/me` | Информация о владельце |
| GET | `/health` | Проверка доступности сервиса |
| GET | `/notes` | Получение заметок |
| POST | `/notes` | Создание заметки |
| GET | `/secret/{key}` | Проверка секретного ключа |
| GET | `/weather/{city}` | Получение информации о погоде |
| GET | `/docs` | Интерактивная документация API |

Примеры запросов:

```bash
curl http://localhost:5458/

curl http://localhost:5458/me

curl -X POST http://localhost:5458/notes \
  -H "Content-Type: application/json" \
  -d '{"text": "ЛР2: сборка образа"}'

curl http://localhost:5458/notes

curl http://localhost:5458/secret/your_secret_key
```

При проверке секретного маршрута используется значение, переданное через `APP_SECRET`.

## 5. Оптимизация Docker-образа

Для оптимизации создан файл `Dockerfile.optimized`.

В нём зависимости копируются отдельно от исходного кода, а установка Python-пакетов выполняется с параметром `--no-cache-dir`.

Сборка второй версии:

```bash
docker build -t rekun-assistant:v2 -f Dockerfile.optimized .
```

Сравнение размеров:

```bash
docker images | grep rekun-assistant
```

Полученные результаты:

| Образ | Размер |
|---|---|
| `rekun-assistant:v1` | 188 МБ |
| `rekun-assistant:v2` | 175 МБ |

Размер образа уменьшился на 13 МБ, или приблизительно на 6,9%.

Отдельное копирование `requirements.txt` также позволяет повторно использовать кешированный слой установки зависимостей при изменениях исходного кода приложения.
### Многостадийная сборка

В дополнение к базовой оптимизации реализована многостадийная сборка Docker-образа.

В `Dockerfile.optimized` используются две стадии:

- `builder` — установка зависимостей Python в отдельный каталог `/install`.
- `runner` — формирование окружения запуска приложения с копированием установленных зависимостей из первой стадии.

В итоговом образе сохранены персональный порт `5458`, переменные окружения приложения и проверка состояния через `HEALTHCHECK`.

Сборка образа:

```bash
docker build -t rekun-assistant:multistage -f Dockerfile.optimized .
```

В результате получен образ размером 178 МБ.

| Версия образа | Размер |
|---|---:|
| `v1` — базовый образ | 188 МБ |
| `v2` — оптимизация pip | 175 МБ |
| `v3` — сборка с `.dockerignore` | 188 МБ |
| `multistage` — многостадийная сборка | 178 МБ |

Многостадийная сборка позволила разделить установку зависимостей и формирование итогового контейнера. Размер по сравнению с базовой версией уменьшился на 10 МБ.

При этом версия `v2` осталась наиболее компактной среди полученных образов.
## 6. Использование .dockerignore

Для исключения ненужных файлов из контекста сборки создан `.dockerignore`.

Из контекста исключаются файлы кеша Python, локальные виртуальные окружения, журналы, данные Git и вспомогательные файлы.

После создания `.dockerignore` выполнена повторная сборка:

```bash
docker build -t rekun-assistant:v3 .
```

## 7. Настройка Healthcheck

В окончательную конфигурацию `Dockerfile.optimized` добавлена проверка состояния приложения через маршрут `/health`.

Для выполнения проверки внутри образа устанавливается утилита `curl`.

Параметры Healthcheck:

- Интервал проверки — 30 секунд.
- Тайм-аут — 5 секунд.
- Начальный период — 10 секунд.
- Количество допустимых неудачных проверок — 3.

Сборка финального образа:

```bash
docker build -t rekun-assistant:final -f Dockerfile.optimized .
```

Перед запуском финального контейнера необходимо освободить порт 5458, если он занят другим сервисом.

Запуск:

```bash
docker run -d \
  --name rekun-assistant-final \
  -p 5458:5458 \
  -e APP_OWNER=rekun \
  -e APP_SECRET=your_secret_key \
  rekun-assistant:final
```

Проверка состояния:

```bash
docker ps --filter "name=rekun-assistant-final" \
  --format "table {{.Names}}\t{{.Status}}"
```

При выполнении лабораторной контейнер получил статус `healthy`, подтверждающий успешное прохождение проверки.

## 8. Тегирование образа

Для финального образа создаются дополнительные теги:

```bash
docker tag rekun-assistant:final rekun-assistant:1.0.0

docker tag rekun-assistant:final \
  rekun-assistant:$(date +%Y%m%d)
```

Просмотр образов:

```bash
docker images | grep rekun-assistant
```

По результатам работы созданы образы `v1`, `v2`, `v3`, `final`, `1.0.0` и тег с датой сборки.

## 9. Результат выполнения

В ходе лабораторной работы выполнена контейнеризация FastAPI-приложения, исследована оптимизация размера Docker-образа, настроено исключение файлов из контекста сборки и добавлена автоматическая проверка состояния сервиса.

Работоспособность приложения подтверждена HTTP-запросами, а состояние финального контейнера — статусом `healthy`.

Выполнено тегирование финального образа для идентификации версии и даты сборки.

## Лабораторная работа 3

Настроены PostgreSQL, постоянное хранение заметок через Docker volume, bind mount и отдельная сеть Docker.
## Лабораторная работа 3. Хранение данных и Docker-сети

В третьей лабораторной работе к приложению Personal Assistant подключена база данных PostgreSQL. Настроено постоянное хранение заметок, подключение конфигурационного файла и взаимодействие контейнеров через отдельную Docker-сеть.

### 1. PostgreSQL и Docker volume

Для хранения данных используется PostgreSQL 16, запущенный в контейнере `rekun-postgres`.

Создан Docker volume `rekun-pgdata`, который подключён к каталогу `/var/lib/postgresql/data` внутри контейнера базы данных.

Параметры базы данных:

- Имя контейнера: `rekun-postgres`
- Имя базы: `rekun28`
- Пользователь: `rekun`
- Порт: `5458:5432`
- Volume: `rekun-pgdata`

Проверка работы PostgreSQL:

`docker exec rekun-postgres pg_isready -U rekun -d rekun28`

### 2. Подключение приложения

В приложение добавлен файл `app/database.py`, содержащий подключение к PostgreSQL и создание таблицы `notes`.

Для работы с базой данных в `requirements.txt` добавлена библиотека `psycopg2-binary`.

Приложение запускается в контейнере `rekun-assistant-lab3` и доступно через порт `8028`.

### 3. Проверка сохранения заметок

Для создания и просмотра заметок используются маршруты:

- `POST /notes` — создание заметки.
- `GET /notes` — получение всех сохранённых заметок.

После создания заметки контейнер приложения был остановлен, удалён и создан заново.

Повторная проверка показала, что заметка сохранилась в PostgreSQL. Это подтверждает, что данные больше не зависят от жизненного цикла контейнера приложения.

### 4. Bind mount

Создан конфигурационный файл `config/app.conf`, содержащий основные параметры приложения.

Файл подключён внутрь проверочного контейнера через bind mount в режиме `readonly`.

Содержимое файла внутри контейнера проверено командой:

`docker exec rekun-config-check cat /app/config/app.conf`

Проверка подтвердила, что файл с компьютера доступен внутри контейнера.

### 5. Docker-сеть

Создана пользовательская сеть `rekun-backend` с драйвером `bridge`.

К сети подключены контейнеры `rekun-postgres` и `rekun-assistant-lab3`.

Приложение обращается к базе данных по имени `rekun-postgres` через внутренний порт `5432`.

При проверке сети:

- Внутри `rekun-backend` PostgreSQL доступен по адресу `172.18.0.2`.
- Из стандартной сети `bridge` ICMP-пакеты до этого адреса не дошли.

Таким образом, проверена связь контейнеров внутри пользовательской сети и отсутствие ICMP-доступа в проведённом тесте из стандартной сети.

### 6. Основные команды проверки

Проверка работающих контейнеров:

`docker ps`

Просмотр Docker volumes:

`docker volume ls`

Просмотр Docker-сетей:

`docker network ls`

Проверка сохранённых заметок:

`curl http://localhost:8028/notes`

Проверка состояния приложения:

`curl http://localhost:8028/health`
### 7. Запуск лабораторной работы

Перед запуском необходимо установить Docker и перейти в папку `solutions/assist-py`.

**Создание хранилища и сети:**

```bash
docker volume create rekun-pgdata
docker network create rekun-backend
```

**Запуск PostgreSQL:**

```bash
docker run -d \
  --name rekun-postgres \
  --network rekun-backend \
  -e POSTGRES_USER=rekun \
  -e POSTGRES_PASSWORD=rekun28pass \
  -e POSTGRES_DB=rekun28 \
  -p 5458:5432 \
  -v rekun-pgdata:/var/lib/postgresql/data \
  postgres:16
```

Проверка готовности базы данных:

```bash
docker exec rekun-postgres pg_isready -U rekun -d rekun28
```

**Сборка приложения:**

```bash
docker build --pull=false -t rekun-assistant:lab3 .
```

**Запуск FastAPI:**

```bash
docker run -d \
  --name rekun-assistant-lab3 \
  --network rekun-backend \
  -p 8028:5458 \
  -e APP_OWNER=rekun \
  -e APP_SECRET=secret28rekun \
  -e DB_HOST=rekun-postgres \
  -e DB_PORT=5432 \
  -e DB_NAME=rekun28 \
  -e DB_USER=rekun \
  -e DB_PASSWORD=rekun28pass \
  rekun-assistant:lab3
```

**Проверка приложения:**

```bash
curl http://localhost:8028/health
curl http://localhost:8028/notes
```

Создание заметки:

```bash
curl -X POST http://localhost:8028/notes \
  -H "Content-Type: application/json" \
  -d '{"text":"Проверка PostgreSQL"}'
```

После повторного создания контейнера приложения заметки остаются в базе данных благодаря Docker volume `rekun-pgdata`.

**Проверка bind mount:**

```bash
docker run --rm \
  --mount type=bind,source="$(pwd)/config/app.conf",target=/app/config/app.conf,readonly \
  --entrypoint cat \
  rekun-assistant:lab3 /app/config/app.conf
```

**Проверка Docker-сети:**

```bash
docker run --rm --network rekun-backend alpine:latest ping -c 2 rekun-postgres
```

### Результат

В ходе работы настроены PostgreSQL, постоянное хранение заметок с помощью Docker volume, bind mount и отдельная сеть Docker. Проверено сохранение заметок после пересоздания контейнера приложения и взаимодействие контейнеров по внутренней сети.
