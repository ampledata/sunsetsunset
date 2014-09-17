#!/usr/bin/env python

"""
Generates sunset and time-lapses.

:author: Greg Albrecht <gba@onbeep.com>
:copyright: Copyright 2014 OnBeep, Inc.
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/sunsetsunset>
"""

__author__ = 'Greg Albrecht <gba@onbeep.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2014 OnBeep, Inc.'


import datetime
import json
import os
import sys
import time

import astral
import dropcam
import twitter


OUTPUT_DIR = 'sunsets'


def get_sunset(location=None, solar_depression=None):
    """
    >>> get_sunset('London', solar_depression='civil')
    """
    location = location or 'San Francisco'
    solar_depression = solar_depression or 'civil'

    aao = astral.Astral()
    aao.solar_depression = solar_depression
    location_astral = aao[location]
    location_sun = location_astral.sun(local=True)

    return location_sun['sunset'].strftime('%s')


def capture_image(camera, seconds=None, prefix=None):
    """
    :param camera: Dropcam Camera Object Instance.
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

    camera.set_property('watermark.enabled', 0)

    if os.path.exists(image_path):
        image_stat = os.stat(image_path)
    else:
        image_stat = None

    if not image_stat or not image_stat.st_size:
        try:
            camera.save_image(image_path, width=width, seconds=seconds)
        except dropcam.ConnectionError as ex:
            print "%s@%s (%s) Error: %s" % (camera.name, seconds, prefix, ex)
            return

        return image_path



def get_cameras(username=None, password=None):
    """
    Returns dropcam cameras.

    >>> get_cameras()
    """
    username = username or os.environ['DROPCAM_USERNAME']
    password = password or os.environ['DROPCAM_PASSWORD']

    dco = dropcam.Dropcam(username, password)

    return dco.cameras()


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

    camera.set_property('watermark.enabled', 0)

    while tl_start < ts:
        image_name = '.'.join([str(tl_start), 'jpg'])
        image_path = os.path.join(image_dir, image_name)

        if os.path.exists(image_path):
            image_stat = os.stat(image_path)
        else:
            image_stat = None

        if not image_stat or not image_stat.st_size:
            try:
                camera.save_image(image_path, width=width, seconds=tl_start)
            except dropcam.ConnectionError as ex:
                print "%s@%s Error: %s" % (camera.name, tl_start, ex)
        tl_start =  tl_start + 30

    while tl_end > ts:
        image_name = '.'.join([str(tl_end), 'jpg'])
        image_path = os.path.join(image_dir, image_name)

        if os.path.exists(image_path):
            image_stat = os.stat(image_path)
        else:
            image_stat = None

        if not image_stat or not image_stat.st_size:
            try:
                camera.save_image(image_path, width=width, seconds=tl_end)
            except dropcam.ConnectionError as ex:
                print "%s@%s Error: %s" % (camera.name, tl_end, ex)
        tl_end = tl_end - 30


def main():
    solar_depressions = ['astronomical', 'nautical', 'civil']

    cameras = get_cameras()

    for sd in solar_depressions:
        sunset_time = get_sunset(solar_depression=sd)
        for camera in cameras:
            if 'Roof' in camera.name:
                image = capture_image(
                    camera=camera, seconds=sunset_time, prefix=sd)

                if sd == 'civil':
                    if image:
                        touch_file = '.'.join(['twitter', sunset_time, sd])
                        touch_path = os.path.join(
                            OUTPUT_DIR, camera.name, touch_file)

                        if not os.path.exists(touch_path):
                            tr = twitter_post(image, message="Today's Sunset (%s)" % sd)
                            if tr:
                                with open(touch_path, 'w') as twouch:
                                    twouch.write(str(tr))

                    get_timelapse_stills(camera, int(sunset_time))


if __name__ == '__main__':
    #import doctest
    #doctest.testmod()
    sys.exit(main())
