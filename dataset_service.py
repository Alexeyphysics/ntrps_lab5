"""Сервисный модуль работы с файлами датасета и аннотациями.

Лабораторная работа №5 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С. (гр. M_PIN_RIS_2607)
"""

from __future__ import annotations

from pathlib import Path
import random
import shutil
from typing import List, Tuple

import pandas as pd


def create_annotation_file(
    dataset_dir: Path | str,
    output_csv: Path | str,
) -> pd.DataFrame:
    """Формирует CSV-файл аннотации датасета."""
    root_path = Path(dataset_dir).resolve()
    project_root = Path.cwd().resolve()
    records: List[Tuple[str, str, str]] = []

    for class_folder in sorted(root_path.iterdir()):
        if not class_folder.is_dir() or not class_folder.name.isdigit():
            continue
        cls_name = class_folder.name
        for f in sorted(class_folder.glob("*.txt")):
            abs_p = str(f.resolve())
            try:
                rel_p = str(f.relative_to(project_root))
            except ValueError:
                rel_p = str(f)
            records.append((abs_p, rel_p, cls_name))

    cols = ["absolute_path", "relate_path", "output_class"]
    df = pd.DataFrame(data=records, columns=cols)
    out_file = Path(output_csv).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False, encoding="utf-8")
    return df


def copy_dataset_by_class(
    src_dir: Path | str,
    dst_dir: Path | str,
    output_csv: Path | str,
) -> pd.DataFrame:
    """Копирует файлы датасета в формате <class>_<index>.txt."""
    src = Path(src_dir).resolve()
    dst = Path(dst_dir).resolve()
    dst.mkdir(parents=True, exist_ok=True)
    project_root = Path.cwd().resolve()
    records: List[Tuple[str, str, str]] = []

    for class_folder in sorted(src.iterdir()):
        if not class_folder.is_dir() or not class_folder.name.isdigit():
            continue
        cls_name = class_folder.name
        for f in sorted(class_folder.glob("*.txt")):
            target_f = dst / f"{cls_name}_{f.name}"
            shutil.copy2(f, target_f)
            abs_p = str(target_f.resolve())
            try:
                rel_p = str(target_f.relative_to(project_root))
            except ValueError:
                rel_p = str(target_f)
            records.append((abs_p, rel_p, cls_name))

    cols = ["absolute_path", "relate_path", "output_class"]
    df = pd.DataFrame(data=records, columns=cols)
    df.to_csv(Path(output_csv).resolve(), index=False, encoding="utf-8")
    return df


def copy_dataset_random_names(
    src_dir: Path | str,
    dst_dir: Path | str,
    output_csv: Path | str,
) -> pd.DataFrame:
    """Копирует датасет с уникальными номерами 0..10000 без коллизий."""
    src = Path(src_dir).resolve()
    dst = Path(dst_dir).resolve()
    dst.mkdir(parents=True, exist_ok=True)
    project_root = Path.cwd().resolve()

    items: List[Tuple[Path, str]] = []
    for class_folder in sorted(src.iterdir()):
        if not class_folder.is_dir() or not class_folder.name.isdigit():
            continue
        for f in sorted(class_folder.glob("*.txt")):
            items.append((f, class_folder.name))

    if not items:
        return pd.DataFrame()

    rand_nums = random.sample(range(0, 10001), len(items))
    records: List[Tuple[str, str, str]] = []

    for (f, cls_name), num in zip(items, rand_nums):
        target_f = dst / f"{str(num).zfill(5)}.txt"
        shutil.copy2(f, target_f)
        abs_p = str(target_f.resolve())
        try:
            rel_p = str(target_f.relative_to(project_root))
        except ValueError:
            rel_p = str(target_f)
        records.append((abs_p, rel_p, cls_name))

    cols = ["absolute_path", "relate_path", "output_class"]
    df = pd.DataFrame(data=records, columns=cols)
    df.to_csv(Path(output_csv).resolve(), index=False, encoding="utf-8")
    return df
