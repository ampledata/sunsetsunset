#!/usr/bin/env python

"""
Generates sunset and time-lapses.

:author: Greg Albrecht <gba@gregalbrecht.com>
:copyright: Copyright 2015 Greg Albrecht
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/sunsetsunset>
"""


import os
import tempfile
import time

import astral
import requests
import twitter


__author__ = 'Greg Albrecht <gba@gregalbrecht.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2015 Greg Albrecht'


GET_IMAGE_URL = 'https://nexusapi.dropcam.com/get_image?'


def get_sunset(location=None):
    """
    >>> get_sunset('London')
    """
    location = location or 'San Francisco'

    aao = astral.Astral()
    location_astral = aao[location]
    location_sun = location_astral.sun(local=True)

    return location_sun


def capture_image(camera, seconds=None, width=None):
    """
    :param camera: Camera UUID.
    :param seconds: EPOCH time to capture image.
    """
    seconds = seconds or str(time.time())
    width = width or '1080'

    _file_prefix = '_'.join(['sunsetlib', camera, width, seconds, '-'])

    image_path = tempfile.mkstemp(prefix=_file_prefix, suffix='.jpg')[1]

    image_params = {'uuid': camera, 'width': width, 'time': seconds}

    req = requests.get(GET_IMAGE_URL, params=image_params)
    if req.ok:
        with open(image_path, 'w') as image_fd:
            image_fd.write(req.content)
        return image_path


def twitter_post(media, message=None):
    message = message or "Today's Sunset"
    api = twitter.Api(
        consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
        consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
        access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
        access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
    )
    return api.PostMedia(message, media)
