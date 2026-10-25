FROM python:3.11-slim
LABEL maintainer="rekun@lab.local"
LABEL version="1.0"
# Рабочая директория внутри контейнера
WORKDIR /app
# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install -r requirements.txt
# Копирование кода приложения
COPY app/ ./app/
# Персональный порт
EXPOSE 5458
# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5458"]
