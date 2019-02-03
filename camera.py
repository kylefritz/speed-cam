import asyncio
import cv2
import datetime
import imutils
import os
import time

from object_tracker import ObjectTracker

CROP_REMOVE_WARP = (200, 1200, 500, 2000)
CROP_TO_ROAD = (810, 950, 680, 2000)
DEEPCAM_FFSERVER_URL = 'http://deepcam.local:8090/camera.mjpeg'
STORAGE_ROOT = '/mnt/usb-sd'


def crop_remove_warp(im):
    (x0, xf, y0, yf) = CROP_REMOVE_WARP
    return im[x0:xf, y0:yf]


def crop_to_road(im):
    (x0, xf, y0, yf) = CROP_TO_ROAD
    return im[x0:xf, y0:yf]


def blur(im):
    return cv2.GaussianBlur(im, (21, 21), 0)


def flip_and_rotate(im):
    im = cv2.flip(im, -1)
    ROTATE_ANGLE = -9
    return imutils.rotate(im, angle=ROTATE_ANGLE)


def filter_contours(contours):
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
        yield rect


def image_path(capture_time, is_occasional=False):
    folder_name = 'occasionals' if is_occasional else 'tracked'
    base_path = os.path.join(STORAGE_ROOT, folder_name)
    os.makedirs(base_path, exist_ok=True)

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


class SpeedCamera:
    @staticmethod
    async def run(completed_tracks_q):
        robot = SpeedCamera(completed_tracks_q)
        robot.run_loop_forever()

    def __init__(self, completed_tracks_q):
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        self.tracker = ObjectTracker()
        self.completed_tracks_q = completed_tracks_q

    def run_loop_forever(self):
        cam = cv2.VideoCapture(DEEPCAM_FFSERVER_URL)
        while True:
            success, frame = cam.read()
            captured_at = datetime.datetime.now()
            if not success:
                print('failed to read from video stream; sleeping for 5 seconds')
                time.sleep(5)
                continue

            self.process_frame(frame, captured_at)

    def process_frame(self, frame, captured_at):
        frame = flip_and_rotate(frame)

        # tight crop & blur
        cropped = crop_to_road(frame)
        blurred = blur(cropped)  # TODO: why blur going into fgbg?

        # rm background & shadows
        fgmask = self.fgbg.apply(blurred)
        SHADOW_VALUE = 127
        foreground_mask = cv2.threshold(fgmask, SHADOW_VALUE + 1, 255, cv2.THRESH_BINARY)[1]
        foreground_mask = cv2.dilate(foreground_mask, None, iterations=3)
        no_bg_blurred = cv2.bitwise_and(blurred, blurred, mask=foreground_mask)

        # convert to gray before applying find contours
        gray_blurred = cv2.cvtColor(no_bg_blurred, cv2.COLOR_BGR2GRAY)
        contours = cv2.findContours(gray_blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_rectangles = list(filter_contours(contours))

        if len(contour_rectangles) == 0:
            return

        self.tracker.process(cropped, contour_rectangles)

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


async def upload_track_worker(queue):
    while True:
        # Get a "work item" out of the queue.
        work_item = await queue.get()

        print(f'processed {work_item}')

        # Notify the queue that the "work item" has been processed.
        queue.task_done()


async def main():
    tasks = [
        asyncio.create_task(SpeedCamera.run()),
        asyncio.create_task(upload_track_worker())
    ]

    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
