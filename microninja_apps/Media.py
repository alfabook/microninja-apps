# Media.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Functions related to artwork and media resources
# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Traslation in Italia
import os
from gi.repository import Gtk, GdkPixbuf

# TODO: It would be easier to keep this within kano_apps as package
# data so we wouldn't have to resolve the path like that.
MEDIA_LOCS = ['../media', '/usr/share/microninja-apps/media' , '/usr/share/icons/microninja/66x66/apps/', '/usr/share/icons/microninja/66x66/apps/']
APP_ICON_SIZE = 66


def media_dir():
    for path in MEDIA_LOCS:
        if os.path.exists(path):
            return os.path.abspath(path) + '/'

    raise Exception(_('Multimedia files directory not found.'))


def get_app_icon(loc, size=APP_ICON_SIZE):
    try:
        pb = GdkPixbuf.Pixbuf.new_from_file_at_size(loc, size, size)
        icon = Gtk.Image.new_from_pixbuf(pb)
    except:
        icon = Gtk.Image.new_from_icon_name(loc, -1)
        icon.set_pixel_size(size)

    return icon
