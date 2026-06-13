import os
import tempfile
import yt_dlp
import imageio_ffmpeg
from PyQt6.QtCore import QThread, pyqtSignal

class InfoExtractorThread(QThread):
    info_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, url: str, browser: str = None):
        super().__init__()
        self.url = url
        self.browser = browser

    def run(self):
        ydl_opts = {
            'quiet': True,
            'extract_flat': 'in_playlist', # Глубокий парсинг для видео, но быстрый (flat) для плейлистов
            'noplaylist': False, # Разрешаем получение плейлистов!
        }
        deno_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'deno.exe')
        if os.path.exists(deno_path):
            ydl_opts['js_runtimes'] = {'deno': {'path': deno_path}}
            ydl_opts['remote_components'] = ['ejs:github']

        if self.browser:
            try:
                import browser_cookie3
                browser_func = getattr(browser_cookie3, self.browser.lower(), None)
                if browser_func:
                    cj = browser_func(domain_name='vk.com')
                    temp_cookie_fd, temp_cookie_path = tempfile.mkstemp(suffix=".txt")
                    with os.fdopen(temp_cookie_fd, "w", encoding="utf-8") as f:
                        f.write("# Netscape HTTP Cookie File\n")
                        for cookie in cj:
                            domain = cookie.domain
                            incl = 'TRUE' if domain.startswith('.') else 'FALSE'
                            secure = 'TRUE' if cookie.secure else 'FALSE'
                            expires = str(cookie.expires) if cookie.expires else '0'
                            f.write(f"{domain}\t{incl}\t{cookie.path}\t{secure}\t{expires}\t{cookie.name}\t{cookie.value}\n")
                    ydl_opts['cookiefile'] = temp_cookie_path
                else:
                    ydl_opts['cookiesfrombrowser'] = (self.browser,)
            except Exception:
                ydl_opts['cookiesfrombrowser'] = (self.browser,)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.info_signal.emit(info)
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            if 'cookiefile' in ydl_opts and os.path.exists(ydl_opts['cookiefile']):
                try:
                    os.remove(ydl_opts['cookiefile'])
                except:
                    pass

class DownloaderThread(QThread):
    # Сигналы для связи с GUI
    progress_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(str, str) # title, filepath
    error_signal = pyqtSignal(str)

    def __init__(self, url: str, download_dir: str, browser: str = None, quality: str = "Лучшее видео+звук", playlist_items: str = None):
        super().__init__()
        self.url = url
        self.download_dir = download_dir
        self.browser = browser
        self.quality = quality
        self.playlist_items = playlist_items
        self.is_cancelled = False
        self.last_filename = ""

    def run(self):
        # Базовые настройки
        ydl_opts = {
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self.my_hook],
            'quiet': True,
            'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
        }
        deno_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'deno.exe')
        if os.path.exists(deno_path):
            ydl_opts['js_runtimes'] = {'deno': {'path': deno_path}}
            ydl_opts['remote_components'] = ['ejs:github']
        
        if self.playlist_items:
            ydl_opts['playlist_items'] = self.playlist_items
            ydl_opts['noplaylist'] = False
        else:
            ydl_opts['noplaylist'] = True

        # Настройка качества
        if self.quality == "1080p":
            ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
        elif self.quality == "720p":
            ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
        elif self.quality == "480p":
            ydl_opts['format'] = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best'
        elif self.quality == "Только аудио (MP3)":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            # Лучшее видео+звук
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        # Авторизация (куки)
        temp_cookie_path = None
        if self.browser:
            try:
                import browser_cookie3
                browser_func = getattr(browser_cookie3, self.browser.lower(), None)
                if browser_func:
                    cj = browser_func(domain_name='vk.com')
                    temp_cookie_fd, temp_cookie_path = tempfile.mkstemp(suffix=".txt")
                    with os.fdopen(temp_cookie_fd, "w", encoding="utf-8") as f:
                        f.write("# Netscape HTTP Cookie File\n")
                        for cookie in cj:
                            domain = cookie.domain
                            incl = 'TRUE' if domain.startswith('.') else 'FALSE'
                            secure = 'TRUE' if cookie.secure else 'FALSE'
                            expires = str(cookie.expires) if cookie.expires else '0'
                            f.write(f"{domain}\t{incl}\t{cookie.path}\t{secure}\t{expires}\t{cookie.name}\t{cookie.value}\n")
                    ydl_opts['cookiefile'] = temp_cookie_path
                else:
                    ydl_opts['cookiesfrombrowser'] = (self.browser,)
            except Exception:
                ydl_opts['cookiesfrombrowser'] = (self.browser,)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                title = info.get('title', 'Unknown')
                
                # Имя файла для открытия
                if self.quality == "Только аудио (MP3)":
                    ext = "mp3"
                else:
                    ext = info.get('ext', 'mp4')
                
                # Если скачивали плейлист, то info это словарь с записями
                if '_type' in info and info['_type'] == 'playlist':
                    self.finished_signal.emit(f"Успешно скачан плейлист: {title}", self.download_dir)
                else:
                    # Узнаем точный путь к скачанному файлу
                    final_filename = ydl.prepare_filename(info)
                    if self.quality == "Только аудио (MP3)":
                        final_filename = os.path.splitext(final_filename)[0] + ".mp3"
                    self.finished_signal.emit(f"Успешно скачано: {title}", final_filename)
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            if temp_cookie_path and os.path.exists(temp_cookie_path):
                try:
                    os.remove(temp_cookie_path)
                except:
                    pass

    def my_hook(self, d):
        if self.is_cancelled:
            raise Exception("Скачивание отменено пользователем.")
            
        if d['status'] == 'downloading':
            self.progress_signal.emit(d)
        elif d['status'] == 'finished':
            d['status_text'] = 'Пост-обработка (склейка или конвертация)...'
            self.progress_signal.emit(d)

    def cancel(self):
        self.is_cancelled = True
