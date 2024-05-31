import logging
import os
import time
from datetime import datetime, timedelta

UPLOADS_FOLDER = 'uploads'
TTL_MIN = 5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def delete_old_files():
    """
    Deletes files in the UPLOADS_FOLDER that are older than TTL_MIN
    """
    now = datetime.now()
    ttl = timedelta(minutes=TTL_MIN)

    for filename in os.listdir(UPLOADS_FOLDER):
        file_path = os.path.join(UPLOADS_FOLDER, filename)
        if os.path.isfile(file_path):
            file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if now - file_creation_time > ttl:
                try:
                    os.remove(file_path)
                    logging.info(f"Deleted old file: {file_path}")
                except Exception as e:
                    logging.error(f"Error deleting file {file_path}: {e}")


if __name__ == "__main__":
    while True:
        delete_old_files()
        logging.info("Sleeping for 5 minutes")
        time.sleep(60)
