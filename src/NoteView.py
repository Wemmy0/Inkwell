import json
import requests
from gi.repository import GLib, Gtk, GdkPixbuf
from random import randint
import sys


class NoteView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        # self.set_css_name("NoteView")
        self.children = []

    def remove_all(self):
        for i in self.children:
            self.remove(i)
        self.children = []

    def change_file(self, filename):
        self.filename = filename
        self.remove_all()

        with open(filename, "r") as file:
            self.objects = list(json.load(file).values())

        for i in self.objects:
            self.add_element(i)

    def add_element(self, data):
        element = Element(data)
        self.children.append(element)
        self.append(element)

    def save_file(self, *args):
        print(f"Saving {self.filename}")
        out = {}
        with open(self.filename, "w") as file:
            for i in self.children:
                out[randint(0, 9999)] = i.export()
            json.dump(out, file)
            # json.dump(json.dumps(out, indent=4), sys.stdout)


class Element(Gtk.Box):
    def __init__(self, data):
        super().__init__()
        # self.set_child(self)
        # self.set_css_name("NoteElement")
        self.data = data
        match self.data["type"]:
            case "title":
                self.main = Gtk.Entry(text=self.data["text"],
                                      css_name="title",
                                      halign=Gtk.Align.START)
                # TODO: This is bad, but works
                self.main.set_size_request(400, 10)
                # Make read-only:
                # title.set_can_target(False)

            case "body":
                # FIXME
                self.main = Gtk.TextView()
                self.main.get_buffer().set_text(self.data["text"])

            case "image":
                if self.data["source"] == "url":
                    # self.main = Gtk.Spinner(hexpand=True, margin_top=40, margin_bottom=40)
                    # self.main.start()
                    self.main = self.load_image_from_url(self.data["url"])
                    # load_process = Process(target=self.load_image_from_url, args=self.data["url"])
                    # self.load_image_from_url(self.data["source"])
                    # load_process.start()
                    # FIXME: Make image loading asynchronous
                    # load_process.join()

                elif self.data["source"] == "file":
                    self.main = Gtk.Image.new_from_file(self.data["file"])
                    self.main.set_hexpand(True)
                    self.main.set_vexpand(True)
                # TODO: Except file not found

        self.set_tooltip()
        self.append(self.main)

    def export(self):
        out = {}
        out = self.data
        match self.data["type"]:
            case "title":
                out["text"] = self.main.get_text()
            case "body":
                buffer = self.main.get_buffer()
                text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
                out["text"] = text
            case "image":
                pass  # Images can't be changed
        return out

    def load_image_from_url(self, *args):
        url = ""
        for i in args:
            url += i
        try:
            response = requests.get(self.data["url"], allow_redirects=True)
            content = response.content
            loader = GdkPixbuf.PixbufLoader()
            loader.write_bytes(GLib.Bytes.new(content))
            loader.close()
            main = Gtk.Image.new_from_pixbuf(loader.get_pixbuf())
            main.set_hexpand(True)
            main.set_vexpand(True)
        except requests.exceptions.ConnectionError:
            main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                           hexpand=True)
            main.append(Gtk.Image(icon_name="auth-sim-missing-symbolic"))
            main.append(Gtk.Label(label="Unable to get image"))
        return main

    def set_tooltip(self):
        try:
            if self.data["tooltip"]:
                self.set_tooltip_text(self.data["tooltip"])
        except KeyError:
            pass
