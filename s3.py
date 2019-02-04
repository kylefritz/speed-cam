import boto3
import cv2
import tempfile

import paths
from log import log


def upload_image(folder, frame, captured_at):
    # Create an S3 client
    s3 = boto3.client('s3')
    file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=True)
    log.info(f'writing to temp {file.name}')
    write_success = cv2.imwrite(file.name, frame)
    if not write_success:
        log.error(f'couldnt save image to {file.name}')

    s3_key = paths.image_s3_key(folder, captured_at)
    bucket_name = 'slow-down-speed-cam'

    # Uploads the given file using a managed uploader, which will split up large
    # files automatically and upload parts in parallel.
    log.info(f'uploading to s3 {bucket_name}')
    s3.upload_file(file.name, bucket_name, s3_key)
    log.info(f'upload complete')

    return s3_key
