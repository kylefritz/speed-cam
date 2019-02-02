import cv2
import datetime
import imutils
import os
import time
import object_tracker as ot


def crop_remove_warp(im):
    return im[200:1200, 500:2000]


def crop_to_road(im):
    return im[810:950, 680:2000]


def blur(im):
    return cv2.GaussianBlur(im, (21, 21), 0)


def flip_and_rotate(im):
    im = cv2.flip(im, -1)
    ROTATE_ANGLE = -9
    return imutils.rotate(im, angle=ROTATE_ANGLE)


def filter_contours(contours):
    filtered = []
    for c in imutils.grab_contours(contours):
        area = cv2.contourArea(c)
        if area < 4_500:  # too small
            continue
        rect = cv2.boundingRect(c)
        (x, y, w, h) = rect
        if w > 750:  # too wide
            continue
        if h < 80:  # too short
            continue
        filtered.append(rect)
    return filtered


STORAGE_ROOT = '/mnt/usb-sd'
DEEPCAM_FFSERVER_URL = 'http://deepcam.local:8090/camera.mjpeg'
OCCASIONALS_PATH = '{}/occasionals'.format(STORAGE_ROOT)
TRACKED_PATH = '{}/tracked'.format(STORAGE_ROOT)


def image_path(capture_time, is_occasional=False):
    base_path = OCCASIONALS_PATH if is_occasional else TRACKED_PATH
    file_name = '{}.jpg'.format(capture_time.isoformat().replace(':', '_'))
    return os.path.join(base_path, file_name)


def capture_single_image():
    cam = cv2.VideoCapture(DEEPCAM_FFSERVER_URL)
    success, frame = cam.read()
    captured_at = datetime.datetime.now()
    if not success:
        print('occasional image cam.read failed')
        return

    frame = flip_and_rotate(frame)
    frame = crop_remove_warp(frame)

    save_to = image_path(captured_at, is_occasional=True)
    success = cv2.imwrite(save_to, frame)
    print('save=', save_to, ' success=', success)
    return success


def run_camera_loop():
    cam = cv2.VideoCapture(DEEPCAM_FFSERVER_URL)
    fgbg = cv2.createBackgroundSubtractorMOG2()
    tracker = ot.ObjectTracker()

    while True:
        success, frame = cam.read()
        captured_at = datetime.datetime.now()
        if not success:
            print('failed to read from video stream; sleeping for 5 seconds')
            time.sleep(5)
            continue

        frame = flip_and_rotate(frame)

        # tight crop & blur
        cropped = crop_to_road(frame)
        blurred = blur(cropped)

        # rm background & shadows
        fgmask = fgbg.apply(blurred)
        SHADOW_VALUE = 127
        foreground_mask = cv2.threshold(fgmask, SHADOW_VALUE + 1, 255, cv2.THRESH_BINARY)[1]
        foreground_mask = cv2.dilate(foreground_mask, None, iterations=3)
        no_bg_blurred = cv2.bitwise_and(blurred, blurred, mask=foreground_mask)

        # convert to gray before applying find contours
        gray_blurred = cv2.cvtColor(no_bg_blurred, cv2.COLOR_BGR2GRAY)
        contours = cv2.findContours(gray_blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_rectangles = filter_contours(contours)

        if len(contour_rectangles) == 0:
            continue

        # draw tracks on image
        for (x, y, w, h) in contour_rectangles:
            pt1 = (x, y)
            pt2 = (x + w, y + h)
            cv2.rectangle(cropped, pt1, pt2, (255, 0, 255), 2)

        # save tracked
        save_to = image_path(captured_at)
        write_success = cv2.imwrite(save_to, crop_remove_warp(frame))
        if not write_success:
            print('couldnt save image to ', save_to)


if __name__ == "__main__":
    os.makedirs(OCCASIONALS_PATH, exist_ok=True)
    os.makedirs(TRACKED_PATH, exist_ok=True)
    run_camera_loop()
