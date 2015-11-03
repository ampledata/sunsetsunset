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

import sunsetlib


__author__ = 'Greg Albrecht <gba@gregalbrecht.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2015 Greg Albrecht'


OUTPUT_DIR = 'sunset'


def main():
    if sys.argv[1]:
        camera = sys.argv[1]
        message = "Today's Sunset"

        today_sun = sunsetlib.get_sunset()
        sunset_time = today_sun['sunset'].strftime('%s')

        touch_file = '.'.join(['twitter', sunset_time])
        touch_path = os.path.join(OUTPUT_DIR, 'lock', touch_file)

        if int(sunset_time) > int(time.time()) or os.path.exists(touch_path):
            sys.exit(0)

        image_path = sunsetlib.capture_image(camera, seconds=sunset_time)
        if image_path is not None and os.path.exists(image_path):
            tr = sunsetlib.twitter_post(image_path, message)
            os.move(image_path, OUTPUT_DIR)
            if tr:
                with open(touch_path, 'w') as twouch:
                    twouch.write(str(tr))


if __name__ == '__main__':
    sys.exit(main())
