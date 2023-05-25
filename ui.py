from gi.repository import Gtk, Gdk
import json
import os
from os.path import isfile

path = "Folder"

def log(*args):
    if verbose:
        print(*args)


def initialise_json(filename):
    # If json file isn't found, create it with json {}
    with open(filename, "w+") as file:
        file.write("{}")


class LeftWindow(Gtk.Box):
    def __init__(self, path):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)

        # Search bar
        self.search_entry = Gtk.SearchEntry()
        set_margins(self.search_entry, 2)
        self.search_entry.set_placeholder_text("Search Notes/Tasks")
        # self.search_entry.set_tooltip_text("Search Notes/Tasks")
        self.search_entry.connect("search-changed", self.search)

        # Decreasing reduces time to see results, increasing reduces no. of searches
        self.search_entry.set_search_delay(100)

        self.file_viewer = FileViewer(path)

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
                if query.lower() not in files[i].lower():
                    self.file_viewer.get_row_at_index(i).hide()


class FileViewer(Gtk.ListBox):
    def __init__(self, path):
        super().__init__()
        self.set_vexpand(True)
        self.path = path
        self.blacklist = [path + "/colours.json"]

        self.palette = os.listdir("Assets")
        self.files = self.scan_files(path)

        # Remove files that are in the blacklist
        for i in self.blacklist:
            self.files.remove(i)

        self.initialise_colours()
        self.add_files(self.files)

    def scan_files(self, path):
        out = []
        for i in os.listdir(path):
            if not isfile(path + "/" + i):
                out = out + self.scan_files(path + "/" + i)
            else:
                out.append(path + "/" + i)
        log(f"Found {len(out)} files")
        return out

    def add_files(self, files):
        for i in files:
            self.append(FileViewRow(i, self.palette, self.json_data, self.path + "/colours.json"))

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


class FileViewRow(Gtk.Box):
    def __init__(self, filename, palette, current_colours, json_file):
        self.filename = filename
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.palette = palette
        self.popover = Gtk.Popover()

        # Image containing circle, popout to selector of colour
        self.image = Gtk.Image()
        self.current_colours = current_colours
        self.current_colour = "Assets/" + current_colours[self.filename]
        self.image.set_from_file(self.current_colour)
        self.json_file = json_file
        self.colour_popover()

        # TODO: Remove border of button - it's very ugly
        self.colour_button = Gtk.MenuButton(child=self.image)
        self.colour_button.set_popover(self.popover)
        set_margins(self.colour_button, 2)
        self.append(self.colour_button)

        # Box containing file name on the top and start of contents at the button
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        filename_label = Gtk.Label(label=self.filename[self.filename.find("/") + 1:])
        filename_label.set_halign(Gtk.Align.START)
        right_box.append(filename_label)

        preview_label = Gtk.Label(label=self.get_start_contents(self.filename) + "...")
        preview_label.set_sensitive(False)
        preview_label.set_halign(Gtk.Align.START)
        right_box.append(preview_label)

        self.append(right_box)

    def get_start_contents(self, file):
        try:
            with open(file, "r", 20) as content:
                return content.read(20).replace("\n", " ")
        except UnicodeDecodeError:
            print(f"Skipping preview of {file}, not text")
            return ""

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

            # TODO: This should use path provided instead of hard-coded
            with open("Folder/colours.json", "w") as file:
                json.dump(self.current_colours, file)

            self.popover.hide()


class Text:
    def __init__(self):
        self.text_content = ""
        self.pane = Gtk.ScrolledWindow()

        self.viewport = Gtk.Viewport()
        self.pane.set_child(self.viewport)
        self.text = Gtk.TextView()
        self.viewport.set_child(self.text)
        self.buffer = self.text.get_buffer()

        # Removed, sync only on app open/close
        # self.text.connect("backspace", self.detect_changes)
        # self.text.connect("delete-from-cursor", self.detect_changes)

    # def detect_changes(self, widget):
    #     self.text_content = self.buffer.get_text(self.buffer.get_start_iter(),
    #                                              self.buffer.get_end_iter(), False)
    #     log("Changes detected")


def build_ui(window, debug):
    global verbose
    verbose = debug
    log("Building UI...")

    # Custom CSS
    provider = Gtk.CssProvider()
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path('style.css')
    Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider,
                                              Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    header = HeaderUI()
    window.set_titlebar(header)

    main_container = Gtk.Paned()
    main_container.set_position(200)

    # Left pane
    # File viewer
    left_window = Gtk.ScrolledWindow()
    left_viewport = Gtk.Viewport()
    left_window.set_child(left_viewport)

    left_content = LeftWindow(path)
    left_viewport.set_child(left_content)

    main_container.set_start_child(left_window)

    # Right pane
    right = Text()
    main_container.set_end_child(right.pane)

    window.set_child(main_container)


class HeaderUI(Gtk.HeaderBar):
    def __init__(self):
        super().__init__()
        self.set_show_title_buttons(True)

        # New Note Button
        self.new_note_btn = Gtk.Button(icon_name="libreoffice-writer-symbolic",
                                       tooltip_text="New Note")
        self.pack_start(self.new_note_btn)

        # New Task Button
        self.new_task_btn = Gtk.Button(icon_name="checkbox-checked-symbolic",
                                       tooltip_text="New Task")
        self.pack_start(self.new_task_btn)

        # # View mode button (Remove - not a priority)
        # self.view_mode_btn = Gtk.Button()
        # self.view_mode_btn.set_icon_name("org.gnome.gedit-symbolic")
        # self.view_mode_btn.set_tooltip_text("Switch to view mode")
        # self.view_mode_btn.connect("clicked", change_view_mode)
        # self.pack_end(self.view_mode_btn)

        # New Header Button
        self.new_header_btn = Gtk.Button(icon_name="format-text-larger-symbolic",
                                         tooltip_text="Insert Title")
        self.pack_end(self.new_header_btn)

        # New Image Button
        self.new_image_btn = Gtk.Button(icon_name="image-x-generic-symbolic",
                                        tooltip_text="Insert Image")
        self.pack_end(self.new_image_btn)


# def change_view_mode(button):
# 	current_mode = button.get_icon_name()
# 	match current_mode:
# 		case "org.gnome.gedit-symbolic":
# 			# Toggle to view mode
# 			print("Switching to view mode")
# 			button.set_icon_name("ephy-reader-mode-symbolic")
# 			button.set_tooltip_text("Switch to edit mode")
# 		case "ephy-reader-mode-symbolic":
# 			# Toggle to edit mode
# 			print("Switching to edit mode")
# 			button.set_icon_name("org.gnome.gedit-symbolic")
# 			button.set_tooltip_text("Switch to view mode")


def set_margins(widget, num):
    widget.set_margin_start(num)
    widget.set_margin_end(num)
    widget.set_margin_top(num)
    widget.set_margin_bottom(num)
