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
import shutil
import sys
import tempfile
import time

import dropcam


OUTPUT_DIR = '/srv/tomato.28blocks.com/web_root/one_off'


def capture_image(camera, seconds=None, prefix=None):
    """
    :param camera: Dropcam Camera Object Instance.
    :param seconds: EPOCH time to capture image.
    """
    seconds = seconds or str(time.time())
    width = '1080'

    image_dir = os.path.join(OUTPUT_DIR)

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    image_name = '.'.join([camera.name, 'jpg'])

    image_path = os.path.join(image_dir, image_name)

    camera.set_property('watermark.enabled', 0)
    
    temp_file = tempfile.mkstemp()[1]
    
    try:
        camera.save_image(temp_file, width=width, seconds=seconds)
    except dropcam.ConnectionError as ex:
        #print "%s@%s (%s) Error: %s" % (camera.name, seconds, prefix, ex)
        return

    shutil.copyfile(temp_file, image_path)

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


def main():

    cameras = get_cameras()

    for camera in cameras:
        image = capture_image(camera=camera)


if __name__ == '__main__':
    sys.exit(main())
