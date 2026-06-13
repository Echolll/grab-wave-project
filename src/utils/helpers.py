import re

def is_valid_url(url: str) -> bool:
    """Простая проверка, похожа ли строка на URL."""
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def get_default_browser() -> str:
    """Определяет браузер по умолчанию в Windows."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice')
        prog_id, _ = winreg.QueryValueEx(key, 'ProgId')
        
        prog_id = prog_id.lower()
        if 'chrome' in prog_id: return 'chrome'
        if 'opera' in prog_id: return 'opera'
        if 'yandex' in prog_id: return 'yandex'
        if 'edge' in prog_id: return 'edge'
        if 'firefox' in prog_id: return 'firefox'
        if 'safari' in prog_id: return 'safari'
    except Exception:
        pass
    
    return "Нет (без авторизации)"

def open_file_in_explorer(path: str):
    import subprocess
    import os
    if os.name == 'nt':
        # Нормализуем путь для Windows
        path = os.path.normpath(path)
        if os.path.isdir(path):
            subprocess.run(['explorer', path])
        elif os.path.isfile(path):
            subprocess.run(['explorer', '/select,', path])

