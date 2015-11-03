#!/usr/bin/env python

"""
Generates sunset and time-lapses.

:author: Greg Albrecht <gba@gregalbrecht.com>
:copyright: Copyright 2015 Greg Albrecht
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/sunsetsunset>
"""


import os
import shutil
import sys

import sunsetlib


__author__ = 'Greg Albrecht <gba@gregalbrecht.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2015 Greg Albrecht'


OUTPUT_DIR = 'one_off'


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if sys.argv[1]:
        camera = sys.argv[1]
        image_path = sunsetlib.capture_image(camera)
        if image_path is not None and os.path.exists(image_path):
            shutil.move(image_path, OUTPUT_DIR)


if __name__ == '__main__':
    sys.exit(main())
