#!/usr/bin/env python
# -*- coding: utf-8 -*-
# apps.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Traslation in Italian

import os

from microninja.utils import is_running, pkill
from microninja.gtk3.kano_dialog import KanoDialog
from microninja.logging import logger


def run(args):
    app_id = args[0]

    kano_apps = "/usr/bin/python /usr/bin/microninja-apps"
    if is_running(kano_apps):
        pkill(kano_apps)

    return app_id


def launch(app_id):
    cmd = "microninja-apps"
    args = ["install", app_id]

    try:
        #try:
        #    from kano_profile.tracker import track_data
        #    track_data("app-installed", app_id)
        #except Exception:
        #    pass

        os.execvp(cmd, [cmd] + args)
    except:
        logger.error("Unable to launch microninja-apps")
