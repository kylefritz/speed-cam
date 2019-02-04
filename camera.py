import asyncio
import cv2
import datetime
import imutils
import time

from object_tracker import ObjectTracker
from frame import Frame
from log import log
import web_api

DEEPCAM_FFSERVER_URL = 'http://deepcam.local:8090/camera.mjpeg'


class ImagePipeline:
    '''
    Stateful class that updates BackgroundSubtractor & ObjectTracker
    for each frame captured. Enqueues sending frames to s3 and tracks to rails app.
    '''
    def __init__(self, completed_tracks_q, frames_q):
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.tracker = ObjectTracker()
        self.completed_tracks_q = completed_tracks_q
        self.frames_q = frames_q

    def process_frame(self, frame):
        # rm background & shadows to get region proposals
        region_proposals = frame.generate_region_proposals(self.background_subtractor)

        # enqueue save frame to s3 if region proposals found
        if region_proposals:
            self.frames_q.put_nowait(frame)

        # associate region proposals into new & existing tracks
        completed_tracks = self.tracker.process(region_proposals)

        # enqueue save completed tracks to rails
        for track in completed_tracks:
            self.completed_tracks_q.put_nowait(track)


def capture_single_image():
    log.info(f'capturing image')
    cam = cv2.VideoCapture(DEEPCAM_FFSERVER_URL)
    success, image = cam.read()
    captured_at = datetime.datetime.now()
    if not success:
        log.error('occasional image cam.read failed')
        return

    log.info('captured')
    frame = Frame(image, captured_at, is_occasional=True)
    frame.upload_to_s3()


async def image_pipeline(tracks_q, frames_q):
    pipeline = ImagePipeline(tracks_q, frames_q)
    cam = cv2.VideoCapture(DEEPCAM_FFSERVER_URL)
    while True:
        success, image = cam.read()
        captured_at = datetime.datetime.now()
        if not success:
            log.error('failed to read from video stream; sleeping for 5 seconds')
            time.sleep(5)
            continue

        frame = Frame(image, captured_at)
        pipeline.process_frame(frame)


async def frame_s3_worker(queue):
    while True:
        frame = await queue.get()
        frame.upload_to_s3()
        queue.task_done()


async def track_api_worker(queue):
    while True:
        track = await queue.get()
        web_api.upload_track(track)
        queue.task_done()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tracks_q = asyncio.Queue()
    frames_q = asyncio.Queue()

    loop.run_until_complete(asyncio.gather(
        image_pipeline(tracks_q, frames_q),
        track_api_worker(tracks_q),
        frame_s3_worker(frames_q),
    ))
    loop.close()
