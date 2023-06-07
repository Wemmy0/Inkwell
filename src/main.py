import gi
import sys
import os

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw

from ui import UI
from sync import Sync


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Inkwell - DEV")
        UI(self, verbose)


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.set_default_size(600, 400)
        self.sync = Sync("localhost", "Notes", "root", "NEA", "Folder")
        self.win.present()


def help():
    print("-h or --help : print this help information")
    print("--verbose : enable verbose mode")


global verbose
verbose = "--verbose" in sys.argv

if "-h" in sys.argv or "--help" in sys.argv:
    help()
    exit()

if verbose:
    sys.argv.remove("--verbose")
    print("Verbose enabled")

app = MyApp(application_id="com.tomh.Inkwell")
app.run(sys.argv)
app.sync.do()
