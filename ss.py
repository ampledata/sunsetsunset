#!/usr/bin/env python

"""
Generates sunset and time-lapses.

:author: Greg Albrecht <gba@gregalbrecht.com>
:copyright: Copyright 2015 Greg Albrecht
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/sunsetsunset>
"""


import os
import sys
import time

import astral
import requests
import twitter


__author__ = 'Greg Albrecht <gba@gregalbrecht.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2015 Greg Albrecht'


CAMERA = 'a46f756f5a1247469466ec8975707fbe'
GET_IMAGE_URL = 'https://nexusapi.dropcam.com/get_image?'
OUTPUT_DIR = 'sunsets'


def get_sunset(location=None):
    """
    >>> get_sunset('London')
    """
    location = location or 'San Francisco'

    aao = astral.Astral()
    location_astral = aao[location]
    location_sun = location_astral.sun(local=True)

    return location_sun


def capture_image(camera, seconds=None, prefix=None):
    """
    :param camera: Camera UUID.
    :param seconds: EPOCH time to capture image.
    """
    seconds = seconds or str(time.time())
    width = '1080'

    image_dir = os.path.join(OUTPUT_DIR, camera.name, 'single')

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    if prefix:
        image_name = '.'.join([prefix, seconds, 'jpg'])
    else:
        image_name = '.'.join([seconds, 'jpg'])

    image_path = os.path.join(image_dir, image_name)

    if os.path.exists(image_path):
        image_stat = os.stat(image_path)
    else:
        image_stat = None

    img_params = {
        'uuid': camera,
        'width': width,
        'time': seconds
    }

    if not image_stat or not image_stat.st_size:
        try:
            req = requests.get(GET_IMAGE_URL, params=img_params)
        except Exception as ex:
            print "%s@%s (%s) Error: %s" % (camera, seconds, prefix, ex)
            return

        if req.ok:
            return image_path
        else:
            return


def twitter_post(media, message=None):
    message = message or "Today's Sunset"
    api = twitter.Api(
        consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
        consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
        access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
        access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
    )
    return api.PostMedia(message, media)


def get_timelapse_stills(camera, ts):

    image_dir = os.path.join(OUTPUT_DIR, camera.name, 'time-lapse', str(ts))

    width = '1080'

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    time_lapse_span = 3600
    tl_start = ts - time_lapse_span
    tl_end = ts + time_lapse_span

    while tl_start < ts:
        image_name = '.'.join([str(tl_start), 'jpg'])
        image_path = os.path.join(image_dir, image_name)

        if os.path.exists(image_path):
            image_stat = os.stat(image_path)
        else:
            image_stat = None

        img_params = {
            'uuid': camera,
            'width': width,
            'time': tl_start
        }

        if not image_stat or not image_stat.st_size:
            try:
                requests.get(GET_IMAGE_URL, params=img_params)
            except Exception as ex:
                print "%s@%s Error: %s" % (camera, tl_start, ex)
        tl_start = tl_start + 30

    while tl_end > ts:
        image_name = '.'.join([str(tl_end), 'jpg'])
        image_path = os.path.join(image_dir, image_name)

        if os.path.exists(image_path):
            image_stat = os.stat(image_path)
        else:
            image_stat = None

        img_params = {
            'uuid': camera,
            'width': width,
            'time': tl_end
        }

        if not image_stat or not image_stat.st_size:
            try:
                requests.get(GET_IMAGE_URL, params=img_params)
            except Exception as ex:
                print "%s@%s Error: %s" % (camera, tl_end, ex)
        tl_end = tl_end - 30


def main():
    message = "Today's Sunset"

    today_sun = get_sunset()
    sunset_time = today_sun['sunset'].strftime('%s')

    touch_file = '.'.join(['twitter', sunset_time])
    touch_path = os.path.join(OUTPUT_DIR, 'lock', touch_file)

    if int(sunset_time) > int(time.time()) or os.path.exists(touch_path):
        sys.exit(0)

    image = capture_image(camera=CAMERA, seconds=sunset_time)
    if image:
        tr = twitter_post(image, message)
        if tr:
            with open(touch_path, 'w') as twouch:
                twouch.write(str(tr))


if __name__ == '__main__':
    sys.exit(main())
