import requests
import os

from log import log

API_HOSTNAME = "https://speed-cam.herokuapp.com/"

def upload_track(track):
    log.warn(f'upload {track.id} to web api')
    url = os.path.join(API_HOSTNAME, 'tracks')
    payload = track.to_dict()
    return requests.post(url, json=payload)
