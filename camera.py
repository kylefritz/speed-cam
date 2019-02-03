import asyncio
import cv2
import datetime
import imutils
import os
import time
import logging

from object_tracker import ObjectTracker
from log import log
import paths
import s3

CROP_REMOVE_WARP = (200, 1200, 500, 2000)
CROP_TO_ROAD = (810, 950, 680, 2000)
DEEPCAM_FFSERVER_URL = 'http://deepcam.local:8090/camera.mjpeg'


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


def capture_single_image():
    log.info(f'capturing image')
    cam = cv2.VideoCapture(DEEPCAM_FFSERVER_URL)
    success, frame = cam.read()
    captured_at = datetime.datetime.now()
    if not success:
        log.error('occasional image cam.read failed')
        return

    frame = flip_and_rotate(frame)
    frame = crop_remove_warp(frame)
    log.info(f'captured')

    s3.upload_image('occasional', frame, captured_at)

    # save_to = paths.image_path('occasional', captured_at)
    # success = cv2.imwrite(save_to, frame)
    # log.info('save=', save_to, ' success=', success)


class SpeedCamera:
    @staticmethod
    async def run(completed_tracks_q, frames_q):
        robot = SpeedCamera(completed_tracks_q, frames_q)
        robot.run_loop_forever()

    def __init__(self, completed_tracks_q, frames_q):
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        self.tracker = ObjectTracker()
        self.completed_tracks_q = completed_tracks_q
        self.frames_q = frames_q

    def run_loop_forever(self):
        cam = cv2.VideoCapture(DEEPCAM_FFSERVER_URL)
        while True:
            success, frame = cam.read()
            captured_at = datetime.datetime.now()
            if not success:
                log.error('failed to read from video stream; sleeping for 5 seconds')
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

        completed_tracks = self.tracker.process(cropped, contour_rectangles)
        for track in completed_tracks:
            self.completed_tracks_q.put_nowait(track)

        if not contour_rectangles:
            return

        # save frame
        self.frames_q.put_nowait((captured_at, crop_remove_warp(frame)))


async def frame_s3_worker(queue):
    while True:
        track = await queue.get()  # Get work item from queue
        s3.upload_image('tracked', frame, captured_at)
        queue.task_done()  # Notify queue that work item processed


async def track_api_worker(queue):
    while True:
        track = await queue.get()  # Get work item from queue
        log.warn(f'upload to rails? {track.id}')
        queue.task_done()  # Notify queue that work item processed


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tracks_q = asyncio.Queue()
    frames_q = asyncio.Queue()
    loop.run_until_complete(asyncio.gather(
        SpeedCamera.run(tracks_q, frames_q),
        track_api_worker(tracks_q),
        frame_s3_worker(frames_q),
    ))
    loop.close()
