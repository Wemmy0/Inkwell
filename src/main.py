import gi
from sys import argv
import tomllib

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw

from ui import UI
from sync import Sync


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Inkwell")
        self.ui = UI(self, config, verbose)


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_configuration()
        self.sync = Sync(config["database"], verbose)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.set_default_size(600, 400)
        self.win.present()


class ConfigRegenFail(Exception):
    def __str__(self):
        return ("Unable to regenerate configuration.toml."
                "Check the permissions for configuration file folder.")


def log(text):
    if verbose: print(text)


def help():
    print("-h or --help : print this help information")
    print("--verbose : enable verbose mode")


def load_configuration(retry=False):
    global config
    log("Loading configuration file...")
    try:
        with open("configuration.toml", "rb") as config_file:
            config = tomllib.load(config_file)
    except FileNotFoundError:
        if not retry:
            try:
                log("WARNING: Configuration file missing, regenerating")
                with open("src/configuration-default.toml", "r") as default:
                    with open("configuration.toml", "w+") as new:
                        new.writelines(default.readlines())
                    load_configuration(True)
            except:
                raise ConfigRegenFail
        else:
            raise ConfigRegenFail


global verbose
verbose = "--verbose" in argv or "-v" in argv

if "-h" in argv or "--help" in argv:
    help()
    exit()

if verbose:
    argv.remove("--verbose")
    print("Verbose enabled")

app = MyApp(application_id="com.tomh.Inkwell")
app.run(argv)
app.sync.do()
app.sync.close()
