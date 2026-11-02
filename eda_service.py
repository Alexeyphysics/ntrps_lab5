"""Сервисный модуль исследовательского анализа данных (EDA) и NLP.

Лабораторная работа №5 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С. (гр. M_PIN_RIS_2607)
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
from typing import Dict, List, Tuple

import matplotlib
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
import pandas as pd
import pymorphy3
import seaborn as sns

# Безопасный бэкенд для исключения конфликта потоков с PySide6
matplotlib.use("Agg")

try:
    _STOP_WORDS = set(stopwords.words("russian"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    _STOP_WORDS = set(stopwords.words("russian"))

_MORPH = pymorphy3.MorphAnalyzer()


def load_dataset_dataframe(dataset_dir: Path | str) -> pd.DataFrame:
    """Загружает текстовые отзывы из каталога в DataFrame.

    :param dataset_dir: Путь к папке датасета с подкаталогами 1..5.
    :return: DataFrame с колонками rating, title, text, word_count.
    """
    root_path = Path(dataset_dir).resolve()
    # Защита от несуществующего каталога (негативный сценарий)
    if not root_path.exists() or not root_path.is_dir():
        return pd.DataFrame(
            columns=["rating", "title", "text", "word_count"]
        )

    records: List[Tuple[int, str, str]] = []
    for folder in sorted(root_path.iterdir()):
        if folder.is_dir() and folder.name.isdigit():
            rating = int(folder.name)
            for f in sorted(folder.glob("*.txt")):
                try:
                    lines = f.read_text(
                        encoding="utf-8"
                    ).strip().split("\n", 1)
                    title = lines[0].strip() if lines else "Без заголовка"
                    body = lines[1].strip() if len(lines) > 1 else ""
                    if body:
                        records.append((rating, title, body))
                except OSError:
                    continue

    df = pd.DataFrame(records, columns=["rating", "title", "text"])
    if not df.empty:
        df["word_count"] = df["text"].apply(
            lambda t: len(re.findall(r"\b\w+\b", str(t)))
        )
    else:
        df["word_count"] = 0
    return df


def get_dataset_statistics(df: pd.DataFrame) -> str:
    """Формирует текстовый отчет описательной статистики по датасету.

    :param df: Исходный DataFrame.
    :return: Строка с форматированной таблицей описательной статистики.
    """
    if df.empty:
        return "Датасет пуст или не содержит данных."

    stats = df[["rating", "word_count"]].describe().to_string()
    grouped = df.groupby("rating")["word_count"].agg(
        ["count", "mean", "median", "min", "max"]
    ).to_string()

    return (
        f"=== ОПИСАТЕЛЬНАЯ СТАТИСТИКА ===\n{stats}\n\n"
        f"=== СТАТИСТИКА ПО ОЦЕНКАМ ===\n{grouped}"
    )


def generate_boxplot_image(
    df: pd.DataFrame,
    output_path: Path | str = "boxplot_gui.png",
) -> str:
    """Генерирует и сохраняет график Boxplot распределения слов.

    :param df: Исходный DataFrame.
    :param output_path: Путь для сохранения графика.
    :return: Строковый путь к сохраненному изображению.
    """
    out_file = Path(output_path).resolve()
    plt.figure(figsize=(7, 4))
    sns.boxplot(
        data=df,
        x="rating",
        y="word_count",
        hue="rating",
        palette="Set2",
        legend=False,
    )
    plt.title("Распределение количества слов в отзывах по оценкам")
    plt.xlabel("Оценка (★)")
    plt.ylabel("Количество слов")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(out_file, dpi=150)
    plt.close()
    return str(out_file)


def get_top_lemmas_by_class(
    df: pd.DataFrame,
    rating: int,
    top_n: int = 15,
) -> Dict[str, int]:
    """Выполняет лемматизацию и возвращает топ-N слов для класса.

    :param df: DataFrame с отзывами.
    :param rating: Выбранный класс рейтинга (1..5).
    :param top_n: Количество наиболее частых слов.
    :return: Словарь вида {лемма: частота}.
    """
    subset = df[df["rating"] == rating]
    if subset.empty:
        return {}

    custom_stops = _STOP_WORDS.union({
        "это", "свой", "который", "весь", "мочь", "год",
        "достоинство", "недостаток", "сбербанк", "банк",
        "сбер", "отзыв", "очень", "просто", "также", "день",
        "карта", "деньга", "работа"
    })
    lemmas: List[str] = []

    for text in subset["text"]:
        words = re.findall(r"[а-яёА-ЯЁ]{3,}", str(text).lower())
        for w in words:
            if w not in custom_stops:
                norm = _MORPH.parse(w)[0].normal_form
                if norm not in custom_stops and len(norm) > 2:
                    lemmas.append(norm)

    return dict(Counter(lemmas).most_common(top_n))


def generate_word_freq_barchart(
    word_freq: Dict[str, int],
    rating: int,
    output_path: Path | str = "word_freq_gui.png",
) -> str:
    """Строит горизонтальную столбчатую диаграмму частоты лемм.

    :param word_freq: Словарь частотности слов.
    :param rating: Выбранный рейтинг.
    :param output_path: Путь к файлу сохранения.
    :return: Строковый путь к сохраненному изображению.
    """
    out_file = Path(output_path).resolve()
    if not word_freq:
        return ""

    words = list(word_freq.keys())[::-1]
    counts = list(word_freq.values())[::-1]

    plt.figure(figsize=(7, 4))
    color = "#e74c3c" if rating <= 2 else "#2ecc71"
    bars = plt.barh(words, counts, color=color)
    plt.title(f"Топ-15 лемм в отзывах с оценкой ★ {rating}")
    plt.xlabel("Частота упоминания")
    plt.ylabel("Лемма")
    plt.grid(axis="x", linestyle="--", alpha=0.7)

    for bar in bars:
        w = bar.get_width()
        plt.text(
            w + 0.2,
            bar.get_y() + bar.get_height() / 2,
            str(int(w)),
            va="center",
            fontsize=8,
        )

    plt.tight_layout()
    plt.savefig(out_file, dpi=150)
    plt.close()
    return str(out_file)
