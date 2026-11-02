"""Скрипт генерации проверенного jupyter-ноутбука для ЛР5."""

import ast
import json


def create_lab5_notebook() -> None:
    """Формирует и валидирует lab5_notebook.ipynb."""
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Лабораторная работа №5. Тестирование, развертывание и документация\n",
                "\n",
                "**Дисциплина:** Новые технологии в РПС  \n",
                "**Вариант:** №9 (Текстовые отзывы с сервиса *Otzovik*, классы 1–5 звёзд)  \n",
                "**Выполнил:** студент Кондратенко А.С. (гр. M_PIN_RIS_2607)  \n",
                "\n",
                "--- \n",
                "## Цель работы\n",
                "Комплексная интеграция модулей веб-скрейпинга (ЛР1), реорганизации датасета (ЛР2), "
                "графического интерфейса (ЛР3) и исследовательского анализа данных (ЛР4). "
                "Реализация набора unit-тестов с проверкой позитивных, негативных и граничных сценариев, "
                "подготовка скриптов развертывания (run.bat, run.sh, Dockerfile) и технической документации."
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 0. Подготовка окружения и данных"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "import sys\n",
                "import subprocess\n",
                "from pathlib import Path\n",
                "\n",
                "# Автоматическая установка необходимых пакетов в Google Colab\n",
                "for pkg in ['pymorphy3', 'pytest', 'pytest-cov']:\n",
                "    try:\n",
                "        __import__(pkg)\n",
                "    except ImportError:\n",
                "        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', pkg])\n",
                "\n",
                "# Клонирование репозитория в среду Colab\n",
                "if not Path('dataset').exists():\n",
                "    print('Клонирование репозитория ntrps_lab5 в Google Colab...')\n",
                "    os.system('git clone https://github.com/Alexeyphysics/ntrps_lab5.git _tmp_repo')\n",
                "    if Path('_tmp_repo/dataset').exists():\n",
                "        os.system('cp -r _tmp_repo/dataset ./dataset')\n",
                "        os.system('cp -r _tmp_repo/tests ./tests')\n",
                "        os.system('cp _tmp_repo/*.py ./')\n",
                "        os.system('cp _tmp_repo/pytest.ini ./')\n",
                "    os.system('rm -rf _tmp_repo')\n",
                "\n",
                "print('Среда готова, файлы и датасет успешно загружены!')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "--- \n",
                "## 1. Запуск Unit-тестов (Пункт 2 задания)\n",
                "Прогон набора тестов: позитивные проверки, обработка некорректных путей и StopIteration."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Запуск pytest с выводом детального отчета о прохождении\n",
                "!python3 -m pytest -v tests/test_app.py"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "--- \n",
                "## 2. Проверка сервисов датасета и итератора (ЛР2-ЛР3)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from dataset_service import create_annotation_file\n",
                "from review_iterator import ReviewIterator\n",
                "\n",
                "# 1. Создание аннотации\n",
                "df_annot = create_annotation_file('dataset', 'colab_annotation.csv')\n",
                "print(f'Создана аннотация датасета: {len(df_annot)} записей')\n",
                "display(df_annot.head(5))\n",
                "\n",
                "# 2. Проверка итератора по классу ★ 5\n",
                "it = ReviewIterator('dataset', 5)\n",
                "print(f'\\nВсего файлов класса 5: {len(it)}')\n",
                "path, title, body = next(it)\n",
                "print(f'Первый отзыв:\\nЗаголовок: {title}\\nНачало текста: {body[:120]}...')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "--- \n",
                "## 3. Проверка исследовательского анализа EDA и NLP (ЛР4)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from eda_service import (\n",
                "    load_dataset_dataframe,\n",
                "    get_dataset_statistics,\n",
                "    get_top_lemmas_by_class,\n",
                "    generate_boxplot_image,\n",
                "    generate_word_freq_barchart\n",
                ")\n",
                "from IPython.display import Image, display\n",
                "\n",
                "df = load_dataset_dataframe('dataset')\n",
                "print(get_dataset_statistics(df))\n",
                "\n",
                "# Генерация и отображение Boxplot\n",
                "box_img = generate_boxplot_image(df, 'colab_boxplot.png')\n",
                "display(Image(box_img))\n",
                "\n",
                "# Частотный анализ лемм для 1 звезды\n",
                "lemmas_1 = get_top_lemmas_by_class(df, rating=1, top_n=10)\n",
                "chart_1 = generate_word_freq_barchart(lemmas_1, rating=1, output_path='colab_words_1.png')\n",
                "display(Image(chart_1))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "--- \n",
                "## 4. Архитектура деплоя и развертывания (Пункт 3 и 5 задания)\n",
                "Приложение готово к запуску в различных средах:\n",
                "- **Windows:** запуск в один клик через `run.bat` (автосоздание venv и установка зависимостей);\n",
                "- **Linux:** bash-скрипт `run.sh`;\n",
                "- **Docker:** контейнер на базе `python:3.10-slim` с предустановленными библиотеками Qt и OpenGL."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Демонстрация содержимого файла развертывания run.bat\n",
                "if Path('run.bat').exists():\n",
                "    print('=== СОДЕРЖИМОЕ RUN.BAT ===')\n",
                "    print(Path('run.bat').read_text(encoding='utf-8'))"
            ]
        }
    ]

    for idx, cell in enumerate(cells):
        if cell["cell_type"] == "code":
            raw_code = "".join(cell["source"])
            clean_lines = [
                line for line in raw_code.splitlines()
                if not line.strip().startswith("!") and not line.strip().startswith("%")
            ]
            ast.parse("\n".join(clean_lines))

    notebook_data = {
        "cells": cells,
        "metadata": {"language_info": {"name": "python"}},
        "nbformat": 4,
        "nbformat_minor": 2
    }

    with open("lab5_notebook.ipynb", "w", encoding="utf-8") as f_out:
        json.dump(notebook_data, f_out, ensure_ascii=False, indent=1)

    print("Ноутбук lab5_notebook.ipynb успешно создан и проверен AST-валидатором!")


if __name__ == "__main__":
    create_lab5_notebook()
