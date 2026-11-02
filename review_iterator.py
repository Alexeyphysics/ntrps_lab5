"""Модуль итератора отзывов.

Лабораторная работа №5 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С. (гр. M_PIN_RIS_2607)
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, List, Tuple


def read_review_file(file_path: Path | str) -> Tuple[str, str]:
    """Считывает заголовок и тело отзыва из файла."""
    path = Path(file_path)
    if not path.exists():
        return ("Ошибка", f"Файл не найден: {path}")

    try:
        content = path.read_text(encoding="utf-8").strip()
        lines = content.split("\n", 1)
        title = lines[0].strip() if lines else "Без заголовка"
        body = lines[1].strip() if len(lines) > 1 else ""
        return (title, body)
    except OSError as err:
        return ("Ошибка чтения", str(err))


class ReviewIterator(Iterator[Tuple[str, str, str]]):
    """Класс-итератор для обхода файлов отзывов определенной оценки."""

    def __init__(
        self,
        dataset_dir: Path | str,
        class_label: str | int,
    ) -> None:
        """Инициализация итератора."""
        self.dataset_dir = Path(dataset_dir)
        self.class_label = str(class_label)
        self.files: List[Path] = self._load_file_list()
        self.cursor: int = 0

    def _load_file_list(self) -> List[Path]:
        """Загружает список файлов для текущего класса."""
        folder = self.dataset_dir / self.class_label
        if not folder.exists() or not folder.is_dir():
            return []
        return sorted(list(folder.glob("*.txt")))

    def reset(self) -> None:
        """Сбрасывает указатель в начало списка."""
        self.cursor = 0

    def __iter__(self) -> ReviewIterator:
        """Возвращает сам итератор."""
        return self

    def __next__(self) -> Tuple[str, str, str]:
        """Возвращает кортеж данных или возбуждает StopIteration."""
        if self.cursor >= len(self.files):
            raise StopIteration

        file_path = self.files[self.cursor]
        self.cursor += 1
        title, body = read_review_file(file_path)
        return (str(file_path.resolve()), title, body)

    def __len__(self) -> int:
        """Возвращает количество файлов."""
        return len(self.files)
