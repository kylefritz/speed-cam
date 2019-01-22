import argparse
import http.client
import os
import json
import sys
from pprint import pprint
from collections import namedtuple
from dotenv import load_dotenv


def get_access_token():
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
    json_string = res.read().decode("utf-8")

    # parse json response
    response = json.loads(json_string)
    pprint(response)

    access_token = response.get('access_token')
    if not access_token:
        print('WOMP: couldnt get token. Check ENV variables.')
        print('To get PIN, visit {}'.format(pin_url))
        return 2

    print('save access_token to .env as NEST_ACCESS_TOKEN')
    print(access_token)
    return 0


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--access-token", help="get access token", action="store_true")

    args = parser.parse_args()
    if args.access_token:
        sys.exit(get_access_token())
