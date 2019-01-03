import cv2
import numpy as np
import imutils

def crop_and_rotate(im):
    ROTATE_ANGLE = -9
    rotated = imutils.rotate(im, angle=ROTATE_ANGLE) # rotate
    return rotated[810:950, 680:2000] # clip

def read_road_image(path):
    im = cv2.imread(path)
    if im is None:
        return None
    flipped = cv2.flip(im, -1)
    cropped = crop_and_rotate(flipped)
    return cropped

def nothing(x):
    pass
# Creating a window for later use
cv2.namedWindow('result')

# Starting with 100's to prevent error while masking
h,s,v = 100,100,100
hsv = ['h', 's', 'v']
lows = [l + "_low" for l in hsv]
his = [l + "_hi" for l in hsv]
def read_values(labels):
    return np.array([cv2.getTrackbarPos(l,'result') for l in labels])
        
def update_filter(t=None):

    frame = read_road_image('test-images/2018-12-27T17:08:00.704668.jpg')

    #converting to HSV
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    # get info from track bar and appy to result
    lower = read_values(lows)
    upper = read_values(his)

    # masking algorithm
    road_mask = cv2.inRange(hsv,lower, upper)
    # not_road_mask = cv2.bitwise_not(road_mask)
    result = cv2.bitwise_and(frame, frame, mask = road_mask)

    cv2.imshow('result', result)
    print(lower)
    print(upper)


# Creating track bar
for v in lows:
    cv2.createTrackbar(v, 'result', 0, 255, update_filter)
for v in his:
    cv2.createTrackbar(v, 'result', 255, 255, update_filter)

update_filter()
cv2.waitKey()