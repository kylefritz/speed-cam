import os
import time

STORAGE_ROOT = '/mnt/usb-sd'


def filename(capture_time):
    name = capture_time.isoformat().replace(':', '_')
    return f'{name}.jpg'


def image_path(folder, capture_time):
    base_path = os.path.join(STORAGE_ROOT, folder)
    os.makedirs(base_path, exist_ok=True)
    return os.path.join(base_path, filename(capture_time))


def image_s3_key(folder, capture_time):
    return os.path.join(folder, filename(capture_time))
