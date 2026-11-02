"""Модуль тестирования приложения (Unit Tests).

Лабораторная работа №5 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С. (гр. M_PIN_RIS_2607)
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import pytest

from dataset_service import (
    copy_dataset_by_class,
    copy_dataset_random_names,
    create_annotation_file,
)
from eda_service import (
    get_dataset_statistics,
    get_top_lemmas_by_class,
    load_dataset_dataframe,
)
from review_iterator import ReviewIterator, read_review_file


def test_positive_load_dataset_dataframe() -> None:
    """Позитивный тест: загрузка существующего датасета."""
    df = load_dataset_dataframe("dataset")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "rating" in df.columns
    assert "word_count" in df.columns
    assert df["word_count"].min() > 0


def test_positive_annotation_creation(tmp_path: Path) -> None:
    """Позитивный тест: генерация CSV аннотации."""
    out_csv = tmp_path / "test_annotation.csv"
    df = create_annotation_file("dataset", out_csv)
    assert out_csv.exists()
    assert len(df) > 0
    cols = ["absolute_path", "relate_path", "output_class"]
    assert list(df.columns) == cols


def test_positive_review_iterator_iteration() -> None:
    """Позитивный тест: корректный обход файлов итератором."""
    iterator = ReviewIterator("dataset", "1")
    assert len(iterator) > 0
    file_path, title, body = next(iterator)
    assert Path(file_path).exists()
    assert len(title) > 0
    assert len(body) > 0


def test_positive_lemmatization_nlp() -> None:
    """Позитивный тест: извлечение частотных лемм для 1 звезды."""
    df = load_dataset_dataframe("dataset")
    lemmas = get_top_lemmas_by_class(df, rating=1, top_n=5)
    assert isinstance(lemmas, dict)
    assert len(lemmas) > 0
    assert len(lemmas) <= 5
    for word, count in lemmas.items():
        assert isinstance(word, str)
        assert count > 0


def test_negative_load_nonexistent_dataset() -> None:
    """Негативный тест: чтение из несуществующей директории."""
    df = load_dataset_dataframe("non_existent_folder_12345")
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_negative_iterator_invalid_class() -> None:
    """Негативный тест: обращение к несуществующему классу рейтинга."""
    iterator = ReviewIterator("dataset", "99")
    assert len(iterator) == 0
    with pytest.raises(StopIteration):
        next(iterator)


def test_negative_read_nonexistent_file() -> None:
    """Негативный тест: чтение несуществующего файла отзыва."""
    title, body = read_review_file("non_existent_review.txt")
    assert title == "Ошибка"
    assert "Файл не найден" in body


def test_edge_iterator_stop_iteration() -> None:
    """Исключительная ситуация: полный проход и генерация StopIteration."""
    iterator = ReviewIterator("dataset", "5")
    total = len(iterator)
    for _ in range(total):
        next(iterator)

    with pytest.raises(StopIteration):
        next(iterator)

    iterator.reset()
    assert iterator.cursor == 0
    next(iterator)


def test_edge_empty_dataset_statistics() -> None:
    """Исключительная ситуация: вызов статистики для пустого DF."""
    empty_df = pd.DataFrame(columns=["rating", "word_count"])
    stats_text = get_dataset_statistics(empty_df)
    assert "Датасет пуст" in stats_text


def test_edge_dataset_copy_functions(tmp_path: Path) -> None:
    """Граничный случай: копирование по классам и номерам."""
    dst_class = tmp_path / "dst_class"
    annot_class = tmp_path / "annot_class.csv"
    df_cls = copy_dataset_by_class("dataset", dst_class, annot_class)
    assert len(df_cls) > 0
    assert annot_class.exists()

    dst_rand = tmp_path / "dst_rand"
    annot_rand = tmp_path / "annot_rand.csv"
    df_rand = copy_dataset_random_names("dataset", dst_rand, annot_rand)
    assert len(df_rand) > 0
    assert annot_rand.exists()
