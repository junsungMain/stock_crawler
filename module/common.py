import time
import logging
from datetime import datetime, timedelta
import os

def parse_num_value(value):
    return '0' if value == '-' else value.replace(',','')

def retry_on_failure(func, max_retries=3, delay=1):
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"최대 재시도 실패{args}{str(e)}")
                    return None
                
                time.sleep(delay)
        return None
    return wrapper

def setup_logging_and_cleanup(log_dir="logs", days_to_keep=7):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_filename = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    now = datetime.now()
    for fname in os.listdir(log_dir):
        fpath = os.path.join(log_dir, fname)
        if os.path.isfile(fpath):
            try:
                date_str = fname.split(".")[0]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if now - file_date > timedelta(days=days_to_keep):
                    os.remove(fpath)
                    logging.info(f"오래된 로그 파일 삭제: {fname}")
            except Exception as e:
                logging.warning(f"로그 파일 삭제 중 오류: {fname}, {e}")