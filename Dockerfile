# Базовый образ Python 3.10 Slim
FROM python:3.10-slim

# Установка системных зависимостей для работы Qt/OpenGL в Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование зависимостей и установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY . .

# Команда по умолчанию: прогон автотестов
CMD ["pytest", "-v"]
