#!/usr/bin/python3
import os
import sys
import time
import subprocess
from util import *
ctime = time.time()
appdir = "/usr/share/pardus/pardus-lightdm-greeter/"
os.chdir(appdir)
os.umask(0o077)
try:
    import locale
    from locale import gettext as _

    # Translation Constants:
    APPNAME = "pardus-lightdm-greeter"
    TRANSLATIONS_PATH = "/usr/share/locale"
    locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
    locale.textdomain(APPNAME)
except:
    # locale load issue fix
    def _(msg):
        return msg


os.environ["UBUNTU_MENUPROXY"]=""
os.environ["SESSION_MANAGER"]="lightdm"
if get("touch-mode",False):
    os.environ["GTK_TEST_TOUCHSCREEN"] = "1"
os.environ["GDK_CORE_DEVICE_EVENTS"]="1"
os.system("xhost +local:")
os.system("xset s {0} {0}".format(get("blank-timeout",300)))
autoscale = True
try:
    scale=float(get("scale","1"))
    if scale <= 0 :
        dpi = find_best_dpi()
        scale = dpi / 96
    else:
        dpi = 96 * scale
    if dpi > 480: # max %500
        dpi = 480
    if dpi < 48: # min %50
        dpi = 48
except:
    scale = 1
    dpi = 96

os.system(get("init",""))

if int(scale) == scale:
    #dpi = 96
    autoscale = False
    os.environ["GDK_SCALE"]=str(scale)
    os.environ["GDK_DPI_SCALE"]=str(1/scale)


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

settings = Gtk.Settings.get_default()
settings.set_property("gtk-theme-name", get("gtk-theme","Adwaita"))
if autoscale:
    settings.set_property("gtk-font-name", "{} {}".format(get("font","Regular"), get("font-size","10")))
else:
    settings.set_property("gtk-font-name", "{} {}".format(get("font","Regular"), int(int(get("font-size","10"))*scale)))
settings.set_property("gtk-icon-theme-name", get("gtk-theme","Adwaita"))
settings.set_property("gtk-application-prefer-dark-theme", get("dark-theme",True))
settings.set_property("gtk-xft-dpi", 1024*dpi)
settings.set_property("gtk-xft-antialias", True)

loaded_modules = []
base_modules = ["lightdm.py","gtkwindow.py", "monitor.py"]
for module in base_modules + os.listdir("module"):
    if module in loaded_modules:
        continue
    if not os.path.isfile("module/{}".format(module)) or not module.endswith(".py"):
        continue
    with open("module/{}".format(module),"r") as f:
        debug("Loading:{}".format(module))
        try:
            exec(f.read())
            if get("load-async",False):
                if module in base_modules:
                    module_init()
                else:
                    GLib.idle_add(module_init)
            else:
                module_init()
            del(module_init)
        except Exception as e:
            print(e,file=sys.stderr)
        loaded_modules.append(module)

ltime = time.time()
os.chdir(os.environ["HOME"])
debug("Loading finished: {}".format(ltime-ctime))
loginwindow.o("ui_window_main").show()
loginwindow.o("ui_window_main").present()
Gtk.main()
