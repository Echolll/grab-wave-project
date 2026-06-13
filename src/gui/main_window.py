import urllib.request
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLineEdit, QPushButton, QProgressBar, QLabel, QMessageBox, QTextEdit,
                               QComboBox, QFileDialog, QCheckBox, QListWidget, QListWidgetItem, QFrame,
                               QToolBar, QDialog)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QAction, QIcon

from src.core.downloader import DownloaderThread, InfoExtractorThread
from src.utils.helpers import is_valid_url, get_default_browser, open_file_in_explorer
from config import DOWNLOAD_DIR

class PlaylistDialog(QDialog):
    def __init__(self, entries, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор видео из плейлиста")
        self.resize(500, 400)
        layout = QVBoxLayout(self)

        info_label = QLabel("Выберите видео, которые хотите скачать:")
        layout.addWidget(info_label)

        self.list_widget = QListWidget()
        for idx, entry in enumerate(entries, start=1):
            # entries могут быть пустыми словарями (например, приватные видео)
            if not entry: continue
            title = entry.get('title', f"Видео {idx}")
            item = QListWidgetItem(f"[{idx}] {title}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, idx) # Сохраняем реальный индекс
            self.list_widget.addItem(item)
        
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("Выбрать всё")
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn = QPushButton("Сбросить")
        deselect_all_btn.clicked.connect(self.deselect_all)
        
        ok_btn = QPushButton("Продолжить скачивание")
        ok_btn.setObjectName("downloadBtn")
        ok_btn.clicked.connect(self.accept)

        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(deselect_all_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def select_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.CheckState.Checked)

    def deselect_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.CheckState.Unchecked)

    def get_selected_indices_string(self):
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(str(item.data(Qt.ItemDataRole.UserRole)))
        return ",".join(selected)

class LogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Логи скачивания")
        self.resize(500, 400)
        layout = QVBoxLayout(self)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

    def append_log(self, text):
        self.log_text.append(text)

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("История загрузок")
        self.resize(500, 400)
        layout = QVBoxLayout(self)
        
        info_label = QLabel("Двойной клик по файлу откроет его в папке:")
        info_label.setStyleSheet("color: #94A3B8; margin-bottom: 5px;")
        layout.addWidget(info_label)
        
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.open_item)
        layout.addWidget(self.history_list)

    def add_item(self, message, filepath):
        item = QListWidgetItem(message)
        item.setData(Qt.ItemDataRole.UserRole, filepath)
        self.history_list.insertItem(0, item)

    def open_item(self, item):
        filepath = item.data(Qt.ItemDataRole.UserRole)
        if filepath and os.path.exists(filepath):
            open_file_in_explorer(filepath)
        else:
            QMessageBox.warning(self, "Ошибка", "Файл или папка не найдены.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GrabWave")
        self.setFixedSize(600, 550)
        
        # Иконка приложения
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.downloader_thread = None
        self.extractor_thread = None
        
        self.url_timer = QTimer()
        self.url_timer.setSingleShot(True)
        self.url_timer.timeout.connect(self.fetch_video_info)
        
        self.current_download_dir = str(DOWNLOAD_DIR)
        self.current_playlist_entries = None

        self.log_dialog = LogDialog(self)
        self.history_dialog = HistoryDialog(self)

        self._setup_ui()

    def _setup_ui(self):
        toolbar = QToolBar("Главная панель")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        folder_action = QAction("📁 Выбрать папку...", self)
        folder_action.triggered.connect(self.select_directory)
        toolbar.addAction(folder_action)
        
        history_action = QAction("📜 История", self)
        history_action.triggered.connect(self.history_dialog.show)
        toolbar.addAction(history_action)

        log_action = QAction("📝 Логи", self)
        log_action.triggered.connect(self.log_dialog.show)
        toolbar.addAction(log_action)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(15)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(320, 180)
        self.thumbnail_label.setStyleSheet("background-color: #1E293B; border-radius: 8px;")
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setText("Вставьте ссылку\nдля превью")
        
        thumb_layout = QHBoxLayout()
        thumb_layout.addStretch()
        thumb_layout.addWidget(self.thumbnail_label)
        thumb_layout.addStretch()
        main_layout.addLayout(thumb_layout)

        self.video_title_label = QLabel("")
        self.video_title_label.setWordWrap(True)
        self.video_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #F8FAFC;")
        main_layout.addWidget(self.video_title_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Вставьте ссылку (YouTube, VK, RuTube и др.)...")
        self.url_input.textChanged.connect(self.on_url_changed)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Лучшее видео+звук", "1080p", "720p", "480p", "Только аудио (MP3)"])
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.url_input, stretch=1)
        input_layout.addWidget(self.quality_combo)
        main_layout.addLayout(input_layout)

        self.auth_checkbox = QCheckBox("🔐 Авторизация браузера (ВК, приватные видео)")
        self.auth_checkbox.setToolTip("Если включено, потребуется закрыть браузер. Выключите для обычных видео с YouTube.")
        self.auth_checkbox.setChecked(False) # По умолчанию выключено, чтобы не ломать публичные видео
        main_layout.addWidget(self.auth_checkbox)

        main_layout.addSpacing(10)

        self.download_btn = QPushButton("Скачать")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.clicked.connect(self.start_download)
        main_layout.addWidget(self.download_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Готов к работе")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #94A3B8;")
        main_layout.addWidget(self.status_label)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения", self.current_download_dir)
        if dir_path:
            self.current_download_dir = dir_path
            QMessageBox.information(self, "Папка изменена", f"Видео будут сохраняться в:\n{dir_path}")

    def on_url_changed(self, text):
        url = text.strip()
        self.current_playlist_entries = None
        if is_valid_url(url):
            self.video_title_label.setText("Загрузка информации...")
            self.thumbnail_label.clear()
            self.url_timer.start(1000)
        else:
            self.video_title_label.setText("")
            self.thumbnail_label.clear()
            self.thumbnail_label.setText("Вставьте ссылку\nдля превью")
            self.url_timer.stop()

    def fetch_video_info(self):
        url = self.url_input.text().strip()
        if not is_valid_url(url): return
        
        browser = None
        if self.auth_checkbox.isChecked():
            browser = get_default_browser()
            if browser == "Нет (без авторизации)": browser = None

        self.extractor_thread = InfoExtractorThread(url, browser)
        self.extractor_thread.info_signal.connect(self.on_info_fetched)
        self.extractor_thread.error_signal.connect(self.on_info_error)
        self.extractor_thread.start()

    def on_info_fetched(self, info):
        # Проверка на плейлист
        if info.get('_type') == 'playlist' and 'entries' in info:
            entries = list(info['entries'])
            if entries:
                self.current_playlist_entries = entries
                title = info.get('title', 'Плейлист')
                self.video_title_label.setText(f"📋 Плейлист: {title} ({len(entries)} видео)")
        else:
            title = info.get('title', 'Без названия')
            self.video_title_label.setText(title)
        
        thumbnail_url = info.get('thumbnail')
        if thumbnail_url:
            try:
                req = urllib.request.Request(thumbnail_url, headers={'User-Agent': 'Mozilla/5.0'})
                data = urllib.request.urlopen(req).read()
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                pixmap = pixmap.scaled(320, 180, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                self.thumbnail_label.setPixmap(pixmap)
            except Exception:
                pass

    def on_info_error(self, error):
        if "Could not copy Chrome cookie database" in error or "Permission denied" in error:
            self.video_title_label.setText("⚠ Ошибка: закройте Chrome!")
            QMessageBox.warning(self, "Закройте браузер Chrome", "Для получения информации о видео (куки) необходимо полностью закрыть браузер Chrome. После этого вставьте ссылку заново.")
        else:
            self.video_title_label.setText("Не удалось получить превью (закрытое видео или плейлист?)")
        self.thumbnail_label.setText("Ошибка")

    def start_download(self):
        url = self.url_input.text().strip()
        if not is_valid_url(url):
            QMessageBox.warning(self, "Ошибка", "Некорректная ссылка.")
            return
            
        playlist_items_str = None
        if self.current_playlist_entries:
            dialog = PlaylistDialog(self.current_playlist_entries, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                playlist_items_str = dialog.get_selected_indices_string()
                if not playlist_items_str:
                    QMessageBox.warning(self, "Отмена", "Вы не выбрали ни одного видео.")
                    return
            else:
                return # Пользователь нажал крестик / отмена

        self.download_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Подготовка к скачиванию...")
        self.log_dialog.append_log(f"--- Запуск скачивания: {url} ---")

        browser = None
        if self.auth_checkbox.isChecked():
            browser = get_default_browser()
            if browser == "Нет (без авторизации)": browser = None
        
        quality = self.quality_combo.currentText()

        self.downloader_thread = DownloaderThread(url, self.current_download_dir, browser, quality, playlist_items_str)
        self.downloader_thread.progress_signal.connect(self.update_progress)
        self.downloader_thread.finished_signal.connect(self.download_finished)
        self.downloader_thread.error_signal.connect(self.download_error)
        self.downloader_thread.start()

    def update_progress(self, data):
        if data.get('status') == 'downloading':
            percent_str = data.get('_percent_str', '0.0%')
            import re
            percent_str = re.sub(r'\x1b\[[0-9;]*m', '', percent_str).replace('%', '').strip()
            try:
                self.progress_bar.setValue(int(float(percent_str)))
            except ValueError:
                pass
                
            speed = re.sub(r'\x1b\[[0-9;]*m', '', data.get('_speed_str', 'N/A'))
            eta = re.sub(r'\x1b\[[0-9;]*m', '', data.get('_eta_str', 'N/A'))
            self.status_label.setText(f"Скачивание... Скорость: {speed} | Осталось: {eta}")
            
        elif data.get('status') == 'finished':
            self.progress_bar.setValue(100)
            self.status_label.setText(data.get('status_text', "Завершение..."))

    def download_finished(self, message, filepath):
        self.log_dialog.append_log(message)
        self.status_label.setText("Готово!")
        
        self.history_dialog.add_item(message, filepath)
        
        QMessageBox.information(self, "Успех", f"{message}\nСохранено в:\n{filepath}")
        self._reset_ui()

    def download_error(self, error_message):
        self.log_dialog.append_log(f"ОШИБКА: {error_message}")
        self.status_label.setText("Ошибка скачивания.")
        
        if "Could not copy Chrome cookie database" in error_message or "Permission denied" in error_message:
            friendly_msg = (
                "Программа не может получить доступ к вашей авторизации (куки), так как браузер Chrome сейчас открыт и блокирует файлы.\n\n"
                "ПОЖАЛУЙСТА, ПОЛНОСТЬЮ ЗАКРОЙТЕ CHROME и попробуйте нажать 'Скачать' еще раз.\n"
                "(Как только скачивание начнется, Chrome можно будет снова открыть)."
            )
            QMessageBox.warning(self, "Закройте браузер Chrome", friendly_msg)
        else:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при скачивании:\n{error_message}")
            
        self._reset_ui()

    def _reset_ui(self):
        self.download_btn.setEnabled(True)
        self.url_input.setEnabled(True)
        self.url_input.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Готов к работе")
