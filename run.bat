@echo off
chcp 65001 > nul
echo ====================================================
echo Запуск приложения: Аналитическая система отзывов
echo Разработчик: Кондратенко А.С. (гр. M_PIN_RIS_2607)
echo ====================================================

if not exist venv (
    echo Создание виртуального окружения...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Установка зависимостей...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo Запуск графического интерфейса...
python main.py
pause
