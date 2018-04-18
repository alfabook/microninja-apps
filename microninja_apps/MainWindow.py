# MainWindow.py
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# The MainWindow class
# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Traslation in Italia
# comment kano-profile
from gi.repository import Gtk, Gdk

from microninja_apps import Media
from microninja_apps.UIElements import Contents
from microninja_apps.AppGrid import Apps
from microninja_apps.AppData import get_applications, refresh_package_list
from microninja_apps.AppInstaller import AppInstaller
from microninja.gtk3.top_bar import TopBar
from microninja.gtk3.application_window import ApplicationWindow
from microninja.gtk3.microninja_dialog import KanoDialog

from microninja_profile.apps import save_app_state_variable, load_app_state_variable

#try:
#    from kano_profile.tracker import Tracker
#    kanotracker = Tracker()
#except:
#    pass


class MainWindow(ApplicationWindow):
    def __init__(self, install=None, icon_only=False, tutorial=False):
        ApplicationWindow.__init__(self, 'App', 755, 588)

        self._install = install
        self._tutorial = tutorial
        self._icon_only = icon_only
        self._last_page = 0

        self.connect("show", self._app_loaded)

        # Destructor
        self.connect('delete-event', Gtk.main_quit)

        self.set_icon_from_file("/usr/share/microninja-desktop/icons/apps.png")

        # Styling
        screen = Gdk.Screen.get_default()
        specific_css_provider = Gtk.CssProvider()
        specific_css_provider.load_from_path(Media.media_dir() +
                                             'css/style.css')
        specific_style_context = Gtk.StyleContext()
        specific_style_context.add_provider_for_screen(
            screen,
            specific_css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        style = self.get_style_context()
        style.add_class('main_window')

        # Setup widgets
        self.set_decorated(True)
        self._top_bar = TopBar("App", self._win_width, False)
        self._top_bar.set_close_callback(Gtk.main_quit)
        self.set_titlebar(self._top_bar)

        self._contents = Contents(self)

        self.set_main_widget(self._contents)

        self.show_apps_view()

    def get_main_area(self):
        return self._contents

    def get_last_page(self):
        return self._last_page

    def set_last_page(self, last_page_num):
        self._last_page = last_page_num

    def show_apps_view(self, button=None, event=None):
        self._top_bar.disable_prev()
        self._apps = apps = Apps(get_applications(), self)
        self.get_main_area().set_contents(apps)

    def refresh(self, category=None):
        for app in get_applications():
            if self._apps.has_app(app):
                self._apps.update_app(app)
            else:
                self._apps.add_app(app)

    def _app_loaded(self, widget):
        if self._install is not None:
            self._install_apps()
        elif self._tutorial:
            self._show_icon_tutorial()

    def _show_icon_tutorial(self):
        if load_app_state_variable('microninja-apps', 'icon-tutorial-shown'):
            return
        else:
            save_app_state_variable('microninja-apps', 'icon-tutorial-shown', True)

        kdialog = KanoDialog(
            _("Add more applications to your desktop"),
            _("Press the '+' button right to the application name to make it appear "
            "in the desktop. To remove it, press 'x'. ")
            ,
            {
                _("OK, GO"): {
                    "return_value": 0,
                    "color": "green"
                }
            },
            parent_window=self
        )
        kdialog.set_action_background("grey")
        kdialog.title.description.set_max_width_chars(40)
        kdialog.run()

    def _install_apps(self):
        pw = None
        for app in self._install:
            inst = AppInstaller(app, self._apps, pw, self)
            inst.set_check_if_installed(True)
            inst.set_icon_only(self._icon_only)
            inst.install()
            pw = inst.get_sudo_pw()

        self.set_last_page(0)
        refresh_package_list()
        self.refresh()