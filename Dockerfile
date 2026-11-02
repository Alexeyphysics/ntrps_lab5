# Базовый стабильный образ Python 3.10 Slim (Debian Bookworm)
FROM python:3.10-slim-bookworm

# Установка системных библиотек для работы Qt и OpenGL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование зависимостей и установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов проекта
COPY . .

# Команда по умолчанию: прогон 10 модульных тестов
CMD ["pytest", "-v"]
