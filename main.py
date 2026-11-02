"""Точка входа для запуска комплексного GUI-приложения ЛР5.

Лабораторная работа №5 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С. (гр. M_PIN_RIS_2607)
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow


def main() -> None:
    """Запуск приложения со стилем Fusion."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
