import requests
import os
import urllib.parse

from log import log

API_HOSTNAME = "https://speed-cam.herokuapp.com/"

def upload_track(track, hostname=API_HOSTNAME):
    log.warning(f'upload track_id={track.id} to web api')
    url = urllib.parse.urljoin(hostname, '/api/tracks')
    payload = track.to_dict()
    return requests.post(url, json=payload)
