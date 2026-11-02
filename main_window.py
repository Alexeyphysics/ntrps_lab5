"""Главное графическое окно приложения (PySide6 / Qt6).

Лабораторная работа №5 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С. (гр. M_PIN_RIS_2607)
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dataset_service import (
    copy_dataset_by_class,
    copy_dataset_random_names,
    create_annotation_file,
)
from eda_service import (
    generate_boxplot_image,
    generate_word_freq_barchart,
    get_dataset_statistics,
    get_top_lemmas_by_class,
    load_dataset_dataframe,
)
from review_iterator import ReviewIterator
from scraper_service import scrape_reviews_batch


class MainWindow(QMainWindow):
    """Главное окно приложения с вкладками управления, просмотра и EDA."""

    def __init__(self) -> None:
        """Инициализация компонентов окна."""
        super().__init__()
        self.setWindowTitle(
            "Аналитическая система отзывов - ЛР5 (Кондратенко А.С.)"
        )
        self.setMinimumSize(950, 750)

        default_dir = Path("dataset").resolve()
        self.current_dataset_dir: Path = (
            default_dir if default_dir.exists() else Path.cwd()
        )

        self.iterators: Dict[str, ReviewIterator] = {}
        self._init_iterators()
        self._init_ui()

    def _init_iterators(self) -> None:
        """Сброс и инициализация итераторов по звездам."""
        self.iterators = {
            str(s): ReviewIterator(self.current_dataset_dir, str(s))
            for s in range(1, 6)
        }

    def _init_ui(self) -> None:
        """Настройка интерфейса с вкладками QTabWidget."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        top_group = QGroupBox("Рабочий каталог датасета")
        top_layout = QHBoxLayout(top_group)
        self.path_display = QLineEdit(str(self.current_dataset_dir))
        self.path_display.setReadOnly(True)
        top_layout.addWidget(self.path_display)

        btn_select = QPushButton("Выбрать папку...")
        btn_select.clicked.connect(self._select_dataset_folder)
        top_layout.addWidget(btn_select)
        main_layout.addWidget(top_group)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.tab_dataset = QWidget()
        self._setup_dataset_tab(self.tab_dataset)
        self.tabs.addTab(self.tab_dataset, "1. Датасет и Скрейпинг (ЛР1-2)")

        self.tab_viewer = QWidget()
        self._setup_viewer_tab(self.tab_viewer)
        self.tabs.addTab(self.tab_viewer, "2. Просмотр отзывов (ЛР3)")

        self.tab_eda = QWidget()
        self._setup_eda_tab(self.tab_eda)
        self.tabs.addTab(self.tab_eda, "3. Анализ и Графики (ЛР4)")

    def _setup_dataset_tab(self, parent: QWidget) -> None:
        """Наполнение вкладки управления датасетом."""
        layout = QVBoxLayout(parent)

        btn_scrape = QPushButton("Запустить Web-Scraping (докачать отзывы)")
        btn_scrape.clicked.connect(self._run_scraper)
        layout.addWidget(btn_scrape)

        btn_annot = QPushButton("Создать CSV файл-аннотацию датасета")
        btn_annot.clicked.connect(self._create_annotation)
        layout.addWidget(btn_annot)

        btn_class = QPushButton("Создать копию: <класс>_<номер>.txt")
        btn_class.clicked.connect(self._create_class_copy)
        layout.addWidget(btn_class)

        btn_rand = QPushButton("Создать копию: случайные номера (0..10000)")
        btn_rand.clicked.connect(self._create_random_copy)
        layout.addWidget(btn_rand)

        layout.addStretch()

    def _setup_viewer_tab(self, parent: QWidget) -> None:
        """Наполнение вкладки просмотра отзывов через итератор."""
        layout = QVBoxLayout(parent)

        btn_panel = QHBoxLayout()
        for star in range(1, 6):
            btn = QPushButton(f"Следующий: ★ {star}")
            btn.clicked.connect(
                lambda ch=False, s=str(star): self._show_next_review(s)
            )
            btn_panel.addWidget(btn)
        layout.addLayout(btn_panel)

        self.info_label = QLabel("Нажмите кнопку класса для просмотра")
        self.info_label.setStyleSheet("font-weight: bold; color: #2980b9;")
        layout.addWidget(self.info_label)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

    def _setup_eda_tab(self, parent: QWidget) -> None:
        """Наполнение вкладки исследовательского анализа данных."""
        layout = QVBoxLayout(parent)

        ctrl_panel = QHBoxLayout()
        btn_stats = QPushButton("Рассчитать статистику (describe)")
        btn_stats.clicked.connect(self._show_eda_stats)
        ctrl_panel.addWidget(btn_stats)

        btn_box = QPushButton("Построить Boxplot длин отзывов")
        btn_box.clicked.connect(self._show_boxplot)
        ctrl_panel.addWidget(btn_box)

        btn_neg = QPushButton("Частотный анализ ★ 1 (NLP)")
        btn_neg.clicked.connect(lambda: self._show_word_freq(1))
        ctrl_panel.addWidget(btn_neg)

        btn_pos = QPushButton("Частотный анализ ★ 5 (NLP)")
        btn_pos.clicked.connect(lambda: self._show_word_freq(5))
        ctrl_panel.addWidget(btn_pos)
        layout.addLayout(ctrl_panel)

        self.eda_text_output = QTextEdit()
        self.eda_text_output.setReadOnly(True)
        self.eda_text_output.setMaximumHeight(180)
        layout.addWidget(self.eda_text_output)

        self.chart_label = QLabel("Здесь будет отображен график")
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.chart_label.setStyleSheet(
            "border: 1px solid #bdc3c7; background: #ffffff;"
        )
        layout.addWidget(self.chart_label)

    def _select_dataset_folder(self) -> None:
        """Выбор папки датасета через диалог."""
        folder = QFileDialog.getExistingDirectory(
            self, "Выберите папку датасета", str(self.current_dataset_dir)
        )
        if folder:
            self.current_dataset_dir = Path(folder).resolve()
            self.path_display.setText(str(self.current_dataset_dir))
            self._init_iterators()

    def _run_scraper(self) -> None:
        """Запуск модуля сбора данных."""
        res = scrape_reviews_batch(
            base_dir=str(self.current_dataset_dir), target_count=50
        )
        QMessageBox.information(
            self, "Скрейпинг завершен", f"Текущий состав датасета:\n{res}"
        )
        self._init_iterators()

    def _create_annotation(self) -> None:
        """Сохранение аннотации датасета."""
        csv_p, _ = QFileDialog.getSaveFileName(
            self, "Сохранить аннотацию", "annotation.csv", "CSV (*.csv)"
        )
        if csv_p:
            df = create_annotation_file(self.current_dataset_dir, csv_p)
            QMessageBox.information(
                self, "Успех", f"Аннотация создана!\nЗаписей: {len(df)}"
            )

    def _create_class_copy(self) -> None:
        """Создание копии класс_номер."""
        target = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if target:
            annot = Path(target) / "annotation_class.csv"
            df = copy_dataset_by_class(
                self.current_dataset_dir, target, annot
            )
            QMessageBox.information(
                self, "Успех", f"Скопировано файлов: {len(df)}"
            )

    def _create_random_copy(self) -> None:
        """Создание копии со случайными номерами."""
        target = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if target:
            annot = Path(target) / "annotation_random.csv"
            df = copy_dataset_random_names(
                self.current_dataset_dir, target, annot
            )
            QMessageBox.information(
                self, "Успех", f"Скопировано файлов: {len(df)}"
            )

    def _show_next_review(self, star: str) -> None:
        """Вывод очередного отзыва через итератор."""
        it = self.iterators.get(star)
        if not it:
            return
        try:
            f_path, title, body = next(it)
            msg = (
                f"Класс ★ {star} | Отзыв {it.cursor}/{len(it)} | "
                f"{Path(f_path).name}"
            )
            self.info_label.setText(msg)
            self.text_area.setPlainText(
                f"ЗАГОЛОВОК:\n{title}\n\nТЕКСТ:\n{body}"
            )
        except StopIteration:
            QMessageBox.information(
                self, "Завершено", f"Отзывы класса ★ {star} исчерпаны!"
            )
            it.reset()

    def _show_eda_stats(self) -> None:
        """Вывод описательной статистики."""
        df = load_dataset_dataframe(self.current_dataset_dir)
        text = get_dataset_statistics(df)
        self.eda_text_output.setPlainText(text)

    def _show_boxplot(self) -> None:
        """Генерация и отображение графика Boxplot."""
        df = load_dataset_dataframe(self.current_dataset_dir)
        if df.empty:
            QMessageBox.warning(self, "Ошибка", "Датасет пуст!")
            return
        img_p = generate_boxplot_image(df, "boxplot_gui.png")
        pix = QPixmap(img_p)
        self.chart_label.setPixmap(
            pix.scaled(
                self.chart_label.width(), 380, Qt.KeepAspectRatio
            )
        )

    def _show_word_freq(self, star: int) -> None:
        """Генерация и отображение частотной гистограммы слов."""
        df = load_dataset_dataframe(self.current_dataset_dir)
        if df.empty:
            QMessageBox.warning(self, "Ошибка", "Датасет пуст!")
            return
        freq = get_top_lemmas_by_class(df, star, top_n=12)
        img_p = generate_word_freq_barchart(
            freq, star, f"top_words_{star}_gui.png"
        )
        if img_p:
            pix = QPixmap(img_p)
            self.chart_label.setPixmap(
                pix.scaled(
                    self.chart_label.width(), 380, Qt.KeepAspectRatio
                )
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
