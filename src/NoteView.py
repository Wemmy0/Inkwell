import json
import requests
from gi.repository import GLib, Gtk, GdkPixbuf


class NoteView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_css_name("NoteView")
        self.children = []

    def remove_all(self):
        for i in self.children:
            self.remove(i)
        self.children = []

    def change_file(self, filename):
        self.remove_all()
        # self.set_selection_mode(Gtk.SelectionMode.NONE)
        # self.set_orientation(Gtk.Orientation.VERTICAL)

        with open(filename, "r") as file:
            self.objects = list(json.load(file).values())

        for i in self.objects:
            self.add_element(Element(i))

    def add_element(self, element):
        self.children.append(element)
        self.append(element)


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
                print("body text")
                self.main = Gtk.TextView()
                self.main.get_buffer().set_text(self.data["text"])

            case "image":
                if self.data["source"] == "url":
                    try:
                        response = requests.get(self.data["url"], allow_redirects=True)
                        content = response.content
                        loader = GdkPixbuf.PixbufLoader()
                        loader.write_bytes(GLib.Bytes.new(content))
                        loader.close()
                        self.main = Gtk.Image.new_from_pixbuf(loader.get_pixbuf())
                        self.main.set_hexpand(True)
                        self.main.set_vexpand(True)
                    except requests.exceptions.ConnectionError:
                        self.main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                            hexpand=True)
                        self.main.append(Gtk.Image(icon_name="auth-sim-missing-symbolic"))
                        self.main.append(Gtk.Label(label="Unable to get image"))

                elif self.data["source"] == "file":
                    self.main = Gtk.Image.new_from_file(self.data["file"])
                    self.main.set_hexpand(True)
                    self.main.set_vexpand(True)
                # TODO: Except file not found

        self.set_tooltip()
        self.append(self.main)

    def set_tooltip(self):
        try:
            if self.data["tooltip"]:
                self.set_tooltip_text(self.data["tooltip"])
        except KeyError:
            pass
