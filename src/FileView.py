from gi.repository import Gtk
import json
import os
from os.path import isfile


def log(*args):
    if verbose:
        print(*args)


class FileWindow(Gtk.Box):
    def __init__(self, path, colour_coding, verbose_mode):
        super().__init__()
        self.path = path
        self.colour_support = colour_coding
        self.creating_new = False
        global verbose
        verbose = verbose_mode
        self.set_orientation(Gtk.Orientation.VERTICAL)

        # Search bar
        self.search_entry = Gtk.SearchEntry()
        set_margins(self.search_entry, 2)
        self.search_entry.set_placeholder_text("Search Notes/Tasks")
        self.search_entry.set_tooltip_text("Tip: You can search by the name of the colour")
        # self.search_entry.set_tooltip_text("Search Notes/Tasks")
        self.search_entry.connect("search-changed", self.search)

        # Decreasing reduces time to see results, increasing reduces no. of searches
        self.search_entry.set_search_delay(100)

        self.file_viewer = FileViewer(path, self.colour_support)

        self.append(self.search_entry)
        self.append(self.file_viewer)

    def search(self, widget):
        # Search for files
        query = self.search_entry.get_text()
        files = self.file_viewer.files

        # Show everything
        for i in range(len(files)):
            self.file_viewer.get_row_at_index(i).show()

        # Check if query has text
        if query:
            # Find rows which don't match the query and hide them
            for i in range(len(files)):
                # Match the query against the filename and the colour if colour support is enabled in config
                if self.colour_support:
                    if query.lower() not in files[i].lower() + " " + self.file_viewer.json_data[files[i]].lower()[:-4]:
                        self.file_viewer.get_row_at_index(i).hide()
                else:
                    if query.lower() not in files[i].lower():
                        self.file_viewer.get_row_at_index(i).hide()

    def add_note(self, *args):
        if not self.creating_new:
            new_row = NewFileRow(self.path)
            self.file_viewer.append(new_row)
            new_row.filename_entry.grab_focus()
            new_row.confirm.connect("clicked", self.create_new_note)
            new_row.filename_entry.connect("activate", self.create_new_note)
            self.creating_new = True  # Block the user from creating another note whilst making another

    def create_new_note(self, *args):
        filename = self.path + "/" + self.file_viewer.get_last_child().get_last_child().get_first_child().get_text() + ".json"
        print(f"Create new file {filename}")
        self.file_viewer.remove(self.get_last_child().get_last_child())
        initialise_json(filename)
        self.file_viewer.add_files([filename])
        self.file_viewer.files.append(filename)
        self.creating_new = False  # Allows user to use create new note button again


class FileViewer(Gtk.ListBox):
    def __init__(self, path, colour_support):
        super().__init__()
        self.set_vexpand(True)
        self.path = path
        self.colour_support = colour_support
        self.blacklist = [path + "/colours.json"]

        self.palette = os.listdir("Assets")
        self.files = self.scan_files(path)

        # Remove files that are in the blacklist
        for i in self.blacklist:
            self.files.remove(i)

        self.initialise_colours()
        self.file_rows = []
        self.add_files(self.files)

    def scan_files(self, path):
        out = []
        extension = ".json"
        for i in os.listdir(path):
            if not isfile(path + "/" + i):
                out = out + self.scan_files(path + "/" + i)
            elif extension in i:
                # Only return .json files
                out.append(path + "/" + i)
        log(f"Found {len(out)} files in {path}")
        return out

    def add_files(self, files):
        for i in files:
            row = FileViewRow(i, self.colour_support, self.palette, self.json_data, self.path + "/colours.json")
            self.append(row)
            self.file_rows.append(self.get_last_child())

    def initialise_colours(self):
        # Load colours.json
        try:
            with open(self.path + "/colours.json", "r+") as file:
                self.json_data = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("Colours.json wasn't found or corrupted. Creating...")
            initialise_json(self.path + "/colours.json")
            # Now created, open the file
            with open(self.path + "/colours.json", "r+") as file:
                self.json_data = json.load(file)

        for i in (set(self.files) - set(self.json_data)):
            # Find files that don't exist in colours.json yet
            # Default new files to Blue.svg
            self.json_data[i] = "Blue.svg"
            with open(self.path + "/colours.json", "w") as file:
                json.dump(self.json_data, file)


class NewFileRow(Gtk.Box):
    def __init__(self, path):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.path = path
        self.filename_entry = Gtk.Entry(placeholder_text="New File",
                                        margin_top=5,
                                        margin_bottom=5,
                                        margin_end=5,
                                        hexpand=True)
        self.append(self.filename_entry)

        self.confirm = Gtk.Button(icon_name="dino-tick-symbolic",
                                  margin_top=5,
                                  margin_bottom=5,
                                  css_classes=["suggested-action"])
        self.append(self.confirm)

    def create(self):
        return self, f"{self.path}/{self.filename_entry.get_text()}"


class FileViewRow(Gtk.Box):
    def __init__(self, filename, colour_support, palette, current_colours, json_file):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.filename = filename
        self.palette = palette
        self.popover = Gtk.Popover()
        set_margins(self, 1)

        # Image containing circle, popout to selector of colour
        self.image = Gtk.Image()
        self.current_colours = current_colours

        try:
            self.current_colour = "Assets/" + current_colours[self.filename]
        except:
            self.current_colour = "Assets/Blue.svg"

        self.image.set_from_file(self.current_colour)
        self.json_file = json_file
        self.colour_popover()

        # TODO: Remove border of button - it's very ugly
        self.colour_button = Gtk.MenuButton(child=self.image, visible=colour_support)
        self.colour_button.set_popover(self.popover)
        self.append(self.colour_button)

        # Box containing file name on the top and start of contents at the button
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.filename_label = Gtk.Label(label=self.filename[self.filename.rfind("/") + 1:].strip(".json"),
                                        margin_start=4)
        self.filename_label.set_halign(Gtk.Align.START)
        right_box.append(self.filename_label)

        last_slash = self.filename.rfind("/")
        if last_slash > -1:
            preview_label = Gtk.Label(label=self.filename[self.filename.find("/"):last_slash].strip(),
                                      margin_start=4)
            preview_label.set_sensitive(False)
            preview_label.set_halign(Gtk.Align.START)
            right_box.append(preview_label)

        self.append(right_box)

    def colour_popover(self):
        container = Gtk.ListBox()

        for i in self.palette:
            container.append(Gtk.Image(file="Assets/" + i))
        container.select_row(container.get_row_at_index(self.palette.index(self.current_colour.replace("Assets/", ""))))
        container.connect("row-selected", self.change_colour)

        self.popover.set_child(container)

    def change_colour(self, container, row):
        new_colour = self.palette[row.get_index()]
        old_colour = self.current_colours[self.filename]

        if new_colour != old_colour:
            self.image.set_from_file("Assets/" + new_colour)
            self.current_colours[self.filename] = self.palette[row.get_index()]

            with open(self.json_file, "w") as file:
                json.dump(self.current_colours, file)

            self.popover.hide()


def initialise_json(filename):
    # If json file isn't found, create it with json {}
    print(f"{filename} doesn't exist. Creating")
    with open(filename, "w+") as file:
        file.write("{}")


def set_margins(widget, x):
    widget.set_margin_start(x)
    widget.set_margin_end(x)
    widget.set_margin_top(x)
    widget.set_margin_bottom(x)
