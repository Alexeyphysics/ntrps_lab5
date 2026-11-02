"""Скрипт автоматизированной сборки автономного исполняемого файла (EXE).

Лабораторная работа №5 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С. (гр. M_PIN_RIS_2607)
Использует PyInstaller для упаковки приложения со всеми зависимостями.
"""

from __future__ import annotations

import subprocess
import sys


def build_standalone_executable() -> None:
    """Запускает PyInstaller для сборки приложения без консоли."""
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=ReviewAnalyticsApp",
        "--add-data=dataset:dataset",
        "main.py",
    ]
    print(f"Сборка исполняемого файла командой:\n{' '.join(cmd)}")
    subprocess.check_call(cmd)
    print("\n[УСПЕХ] Сборка завершена! Исполняемый файл находится в папке dist/")


if __name__ == "__main__":
    build_standalone_executable()
