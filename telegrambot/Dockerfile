# bot/Dockerfile

# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /telegrambot

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в рабочую директорию
COPY . /telegrambot

# Указываем команду для запуска бота
CMD ["python", "trybot.py"]
