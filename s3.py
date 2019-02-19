import boto3
import cv2
import tempfile

from log import log


def upload_image(frame, s3_key):
    # write frame to temporary file
    file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=True)
    log.debug(f'writing to temp {file.name}')
    write_success = cv2.imwrite(file.name, frame)
    if not write_success:
        log.error(f'couldnt save image to {file.name}')

    # Create an S3 client
    s3 = boto3.client('s3')

    # Uploads the given file using a managed uploader, which will split up large
    # files automatically and upload parts in parallel.
    BUCKET_NAME = 'slow-down-speed-cam'
    log.info(f'uploading to s3 {BUCKET_NAME}')
    s3.upload_file(file.name, BUCKET_NAME, s3_key)
    log.debug(f'upload complete')

    return s3_key
