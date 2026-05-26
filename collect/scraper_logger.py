import os

_log_file_path = os.path.join(os.path.dirname(__file__), 'scraper.log')


def log(msg):
    try:
        with open(_log_file_path, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass


def clear_log():
    try:
        if os.path.exists(_log_file_path):
            os.remove(_log_file_path)
    except Exception:
        pass
