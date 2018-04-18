# MainWindow.py
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# A class that handles app installations
#
# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Traslation in Italian
# pass on kano-word

import json
from gi.repository import Gtk, Gdk
from microninja_apps.AppManage import install_app, download_app, AppDownloadError, \
    install_link_and_icon
from microninja_apps.DesktopManage import add_to_desktop
from microninja_apps.AppData import load_from_app_file, is_app_installed
from microninja_apps.UIElements import get_sudo_password
from microninja.gtk3.microninja_dialog import KanoDialog
#from microninja_world.connection import request_wrapper
#from microninja_world.functions import get_glob_session, login_using_token

class AppInstaller:
    def __init__(self, id_or_slug, apps, pw=None, parent_win=None):
        self._handle = id_or_slug
        self._win = parent_win
        self._apps = apps

        self._tmp_data_file = None
        self._tmp_icon_file = None
        self._loc = None
        self._pw = pw

        self._icon_only = False
        self._add_to_desktop = True
        self._check_if_installed = False
        self._report_install = True

    def install(self):
        if self._win is not None:
            self._win.blur()
            self._win.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))

        if not self._download_app():
            return self._end(False)

        if self._check_if_installed:
            if not self._installed_check():
                return self._end(False)

        if not self._get_sudo_pw():
            return self._end(False)

        # Make sure the dialogs are gone before installing
        while Gtk.events_pending():
            Gtk.main_iteration()

        rv = self._install()

        if rv and self._report_install:
            self._report()

        return self._end(rv)

    def set_icon_only(self, v):
        self._icon_only = bool(v)

    def set_add_to_desktop(self, v):
        self._add_to_desktop = bool(v)

    def set_check_if_installed(self, v):
        self._check_if_installed = v

    def set_report_install(self, v):
        self._report_install = v

    def get_loc(self):
        return self._loc

    def get_sudo_pw(self):
        return self._pw

    # Private methods onwards
    def _end(self, rv=True):
        if self._win is not None:
            self._win.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))
            self._win.unblur()

        return rv

    def _download_app(self):
        try:
            app_data_file, app_icon_file = download_app(self._handle)
            self._tmp_data_file = app_data_file
            self._tmp_icon_file = app_icon_file
        except AppDownloadError as err:
            head = _("Cannot download application")
            dialog = KanoDialog(
                head, str(err),
                {
                    "OK": {
                        "return_value": 0
                    },
                },
                parent_window=self._win
            )
            dialog.run()
            del dialog
            return False

        self._app = load_from_app_file(self._tmp_data_file, False)

        return True

    def _installed_check(self):
        if is_app_installed(self._app):
            head = _("{} is already installed").format(self._app["title"])
            desc = _("Do you want to update it?")
            dialog = KanoDialog(
                head, desc,
                {
                    _("YES"): {
                        "return_value": 0
                    },
                    _("NO"): {
                        "return_value": -1
                    }
                },
                parent_window=self
            )
            rv = dialog.run()
            del dialog

            if rv == 0:
                self.set_report_install(False)

            return rv == 0

        return True

    def _get_sudo_pw(self):
        if self._pw is None:
            self._pw = get_sudo_password(_("Install {}").format(self._app["title"]))
            return self._pw is not None

        return True

    def _install(self):
        success = True
        if not self._icon_only:
            success = install_app(self._app, self._pw)

        if success:
            # write out the tmp json
            with open(self._tmp_data_file, "w") as f:
                f.write(json.dumps(self._app))

            self._loc = install_link_and_icon(self._app['slug'],
                                              self._tmp_data_file,
                                              self._tmp_icon_file,
                                              self._pw)

            if not self._icon_only and self._add_to_desktop:
                add_to_desktop(self._app)

            head = _("Done!")
            message = self._app["title"] + _(" successfully installed! ") + \
                _("Find it in the application launcher.")
        else:
            head = _("Installation failed")
            message = self._app["title"] + _(" cannot be installed ") + \
                _("right now. Please check if the device is connected ") + \
                _("to internet and if there is enough free space in ") + \
                _("your sd card.")

        dialog = KanoDialog(
            head,
            message,
            {
                "OK": {
                    "return_value": 0
                },
            },
        )
        dialog.run()
        del dialog

        return success

    def _report(self):
        pass
        #success, value = login_using_token()
        #if success:
        #    endpoint = '/apps/{}/installed'.format(self._app['id'])
        #    gs = get_glob_session()
        #    if gs:
        #        success, text, data = request_wrapper('post', endpoint,
        #                                              session=gs.session)
