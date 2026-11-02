#!/bin/bash
echo "===================================================="
echo "Запуск приложения: Аналитическая система отзывов"
echo "Разработчик: Кондратенко А.С. (гр. M_PIN_RIS_2607)"
echo "===================================================="

if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения venv..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python3 main.py
