from dotenv import load_dotenv
from urllib.parse import urlparse
import argparse
import http.client
import json
import os
import sys


def print_json(thing):
    print(json.dumps(thing, indent=2, sort_keys=True))


def get_access_token():
    # help from: https://github.com/jensmdriller/utility-scripts/blob/master/nest-cam-api/acquire-access-token.py
    CLIENT_ID = os.getenv('NEST_CLIENT_ID')
    CLIENT_SECRET = os.getenv('NEST_CLIENT_SECRET')
    print(CLIENT_ID)
    print(CLIENT_SECRET)

    pin_url = 'https://home.nest.com/login/oauth2?client_id={}&state=STATE'.format(CLIENT_ID)

    PIN = os.getenv('NEST_PIN')
    print(PIN)
    if not PIN:
        print('login to nest then visit {} to get pin'.format(pin_url))
        return 1

    # make request to nest to get access token
    conn = http.client.HTTPSConnection("api.home.nest.com")
    payload = "code={}&client_id={}&client_secret={}&grant_type=authorization_code".format(PIN, CLIENT_ID, CLIENT_SECRET)
    headers = {'content-type': "application/x-www-form-urlencoded"}
    conn.request("POST", "/oauth2/access_token", payload, headers)
    res = conn.getresponse()
    response = json.loads(res.read().decode("utf-8"))
    print_json(response)

    access_token = response.get('access_token')
    if not access_token:
        print('WOMP: couldnt get token. Check ENV variables.')
        print('To get PIN, visit {}'.format(pin_url))
        return 2

    print('save access_token to .env as NEST_ACCESS_TOKEN')
    print(access_token)
    return 0


def read_nest_data():
    access_token = os.getenv('NEST_ACCESS_TOKEN')
    # print(access_token)
    if not access_token:
        print('must use pin to get access token and set in env')
        return 1

    conn = http.client.HTTPSConnection("developer-api.nest.com")
    headers = {'authorization': "Bearer {0}".format(access_token)}
    conn.request("GET", "/", headers=headers)
    response = conn.getresponse()

    # from nest-python3 connection example
    if response.status == 307:
        redirectLocation = urlparse(response.getheader("location"))
        conn = http.client.HTTPSConnection(redirectLocation.netloc)
        conn.request("GET", "/", headers=headers)
        response = conn.getresponse()
        if response.status != 200:
            raise Exception("Redirect with non 200 response")

    nest_data = json.loads(response.read().decode("utf-8"))
    # print_json(nest_data)
    return nest_data


# help from https: // github.com/jensmdriller/utility-scripts/blob/master/nest-cam-api/motion-email-alerts.py
def get_cam_feed():
    nest = read_nest_data()
    camera_id = os.getenv('NEST_CAMERA_ID')
    front_door_cam = nest['devices']['cameras'][camera_id]
    print_json(front_door_cam)

    # front_door_cam['web_url']

    # enabling *public URL* filled in "public_share_url"
    # by poking throught the source in web inspector
    # i was able to find and open an m3u8 stream in VLC player...
    # https://stream-us1-alfa.dropcam.com:443/nexus_aac/<32 character hash>/playlist.m3u8
    os.getenv('NEST_M3U8_ID')

    # would not have needed any of the nest api stuff for that though :)


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--access-token", help="get access token", action="store_true")

    args = parser.parse_args()
    if args.access_token:
        sys.exit(get_access_token())

    get_cam_feed()
