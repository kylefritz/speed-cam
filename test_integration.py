import unittest
import cv2
import datetime
import imutils
import os
import requests

from log import log
from track import Track
from frame import Frame
from region import Region
import web_api


def make_frame(seconds):
    im = cv2.imread('./test-images/calibration.jpg')
    captured_at = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    return Frame(im, captured_at)


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        rectangles = [
            (13, 13, 103, 103),
            (23, 23, 203, 203),
        ]

        self.region1 = Region(rectangles[0], make_frame(0))
        self.track = Track(self.region1)
        self.track.promote()
        self.region2 = Region(rectangles[1], make_frame(0.1))
        self.track.update(self.region2)

    def test_everything_but_post(self):
        assert len(self.track.to_dict()) != 0

    def test_post_track_to_local_rails(self):
        '''
        have to have rails running
        '''
        web_api.upload_track(self.track, "http://localhost:3000")


if __name__ == '__main__':
    unittest.main()
