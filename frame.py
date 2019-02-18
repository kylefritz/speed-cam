import cv2
import datetime
import imutils

from log import log
from region import Region
import paths
import s3
import web_api


class Frame:
    def __init__(self, image, captured_at, is_occasional=False):
        self.image = flip_and_rotate(image)
        self.captured_at = captured_at
        self.is_occasional = is_occasional
        folder = 'occasional' if self.is_occasional else 'tracks'
        self.s3_key = paths.image_s3_key(folder, self.captured_at)

    def upload_to_s3(self):
        s3.upload_image(crop_remove_warp(self.image), self.s3_key)

    def generate_region_proposals(self, background_subtractor):
        # apply tight crop and subtract background
        blurred = blur(crop_to_road(self.image))  # TODO: why blur going into fgbg?
        fgmask = background_subtractor.apply(blurred)
        SHADOW_VALUE = 127
        foreground_mask = cv2.threshold(fgmask, SHADOW_VALUE + 1, 255, cv2.THRESH_BINARY)[1]
        foreground_mask = cv2.dilate(foreground_mask, None, iterations=3)
        no_bg_blurred = cv2.bitwise_and(blurred, blurred, mask=foreground_mask)

        # must convert to gray before finding contours
        gray_blurred = cv2.cvtColor(no_bg_blurred, cv2.COLOR_BGR2GRAY)

        # find and filter region proposals
        contours = cv2.findContours(gray_blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_rectangles = map(cv2.boundingRect, imutils.grab_contours(contours))
        filtered_rectanges = filter(is_reasonable_size, contour_rectangles)

        for rect in filtered_rectanges:
            yield Region(rect, self)


def crop_remove_warp(im):
    CROP_REMOVE_WARP = (200, 1200, 500, 2000)
    (x0, xf, y0, yf) = CROP_REMOVE_WARP
    return im[x0:xf, y0:yf]


def flip_and_rotate(im):
    im = cv2.flip(im, -1)
    ROTATE_ANGLE = -9
    return imutils.rotate(im, angle=ROTATE_ANGLE)


def crop_to_road(im):
    CROP_TO_ROAD = (810, 950, 680, 2000)
    (x0, xf, y0, yf) = CROP_TO_ROAD
    return im[x0:xf, y0:yf]


def blur(im):
    return cv2.GaussianBlur(im, (21, 21), 0)


def is_reasonable_size(rect):
    (x, y, w, h) = rect
    area = w * h
    if area < 4_500:  # too small
        return False
    if w > 750:  # too wide
        return False
    if h < 80:  # too short
        return False
    return True
