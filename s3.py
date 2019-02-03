import boto3
import cv2
import tempfile

import paths


def upload_image(folder, frame, captured_at):
    # Create an S3 client
    s3 = boto3.client('s3')

    file = tempfile.NamedTemporaryFile(delete=True)
    write_success = cv2.imwrite(file.name, frame)
    if not write_success:
        print('couldnt save image to ', file.name)

    s3_key = paths.image_s3_key(folder, captured_at)
    bucket_name = 'slow-down-speed-cam'

    # Uploads the given file using a managed uploader, which will split up large
    # files automatically and upload parts in parallel.
    s3.upload_file(file.name, bucket_name, s3_key)
