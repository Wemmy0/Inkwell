import json
import requests
from gi.repository import GLib, Gtk, GdkPixbuf
from random import randint
from Queue import Stack
import threading
from ChatGPT import AiConnector, AiGUI


def edit_style(element, mode):
    #  Purpose: changes the provided element into edit mode styling.
    #  Mode: True - Change to edit mode, False - Change out of edit mode
    if mode:
        element.set_css_classes(["element-edit"])
        element.controls.show()
    else:
        element.set_css_classes([])
        element.controls.hide()


class NoteView(Gtk.Box):
    def __init__(self, config, ai_config, header):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.config = config
        self.ai_config = ai_config
        self.children = []
        self.header_ui = header
        self.editing = False
        self.history = Stack()

    def remove_all(self):
        for i in self.children:
            self.remove(i)
        self.children = []

    def change_file(self, filename):
        self.filename = filename
        self.remove_all()

        # with open(filename, "w+") as file:
        #     data = file.readlines()
        #     print(data)
        #     if not data:
        #         print(f"{filename} is empty, re-initialising json")
        #         file.write("{}")

        with open(filename, "r") as file:
            # data = file.readlines()
            # print(data)
            # if data == "":
            #     print("Empty File")
            # else:
            self.objects = list(json.load(file).values())

        for i in self.objects:
            self.add_element(i, True)

    def add_element(self, data, loading_file=False):
        element = Element(data, self.config, self.ai_config)
        element.del_btn.connect("clicked", self.remove_element)
        element.up_btn.connect("clicked", self.move)
        element.down_btn.connect("clicked", self.move)
        self.children.append(element)
        self.append(element)
        self.can_move()

        if not loading_file:
            self.header_ui.undo_btn.show()
            self.history.push(self.children[-1])

        if self.editing:  # If in edit mode, new element is also put into edit mode
            edit_style(element, True)

    def undo(self, *args):
        print("Undoing...")
        self.remove(self.history.pop())

        if self.history.is_empty():
            self.header_ui.undo_btn.hide()

    def save_file(self, *args):
        print(f"Saving {self.filename}")
        out = {}
        with open(self.filename, "w") as file:
            for i in self.children:
                out[randint(0, 9999)] = i.export()
            json.dump(out, file)

    def edit(self, *args):
        if not self.editing:
            self.editing = True
            for i in self.children:
                edit_style(i, True)
        else:
            self.editing = False
            for i in self.children:
                edit_style(i, False)
        self.save_file()
        self.change_view_mode()

    def change_view_mode(self):
        current_mode = self.header_ui.edit_btn.get_icon_name()
        match current_mode:
            case "ymuse-edit-symbolic":
                # Toggle to view mode
                self.header_ui.edit_btn.set_icon_name("ephy-reader-mode-symbolic")
                self.header_ui.edit_btn.set_tooltip_text("Switch to view mode")
            case "ephy-reader-mode-symbolic":
                # Toggle to edit mode
                self.header_ui.edit_btn.set_icon_name("ymuse-edit-symbolic")
                self.header_ui.edit_btn.set_tooltip_text("Switch to edit mode")

    def remove_element(self, button):
        element = button.get_parent().get_parent().get_parent()
        element.hide()
        self.children.remove(element)
        self.can_move()
        self.can_undo(element)
        self.save_file()

    def can_undo(self, removed):
        # Purpose: Hides the undo button if all the added elements have been removed
        if self.history.is_empty():
            self.header_ui.undo_btn.hide()
        if all(element not in self.children for element in self.history):
            self.header_ui.undo_btn.hide()

    def move(self, button):
        # Called by either the move up or down button
        # Purpose: Moves elements up or down by swapping them
        element = button.get_parent().get_parent().get_parent()
        row_no = self.children.index(element)
        # Get all children to be affected
        # If up: Gets all the children at one above the moved element and below
        elements = self.children[row_no - 1:] if button.get_icon_name() == "go-up-symbolic" else self.children[row_no:]
        # remove all children one up and the rest below
        for i in elements:
            self.remove(i)
            self.children.remove(i)
        # Swap the first two
        elements[0], elements[1] = elements[1], elements[0]
        # Add them all back
        for i in elements:
            self.append(i)
            self.children.append(i)
        self.can_move()
        self.save_file()

    def can_move(self):
        # Purpose: Make the top and bottom element's respective buttons inactive
        # This stops the highest element being moved up which isn't possible
        try:
            for i in self.children:
                i.up_btn.set_sensitive(True)
                i.down_btn.set_sensitive(True)
            # Get the first and last elements
            self.children[0].up_btn.set_sensitive(False)
            self.children[-1:][0].down_btn.set_sensitive(False)  # Multidimensional array
        except IndexError:
            # If the file is empty - ignore if it errors when trying to set the first and last items as unmovable
            pass


class Element(Gtk.Box):
    def __init__(self, data, config, ai_config):
        super().__init__()
        self.container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.data = data
        self.config = config
        self.ai_config = ai_config
        self.create_controls()
        try:
            match self.data["type"]:
                case "title":
                    if config["title"]: self.main = Title(self.data)
                    self.container.append(self.main)

                case "body":
                    if config["body"]: self.main = Body(self.data)
                    self.container.append(self.main)

                case "image":
                    if config["image"]: self.main = Image(self.data)
                    self.container.append(self.main)

                case "list":
                    if config["list"]: self.main = List(self.data)
                    self.container.append(self.main)

                case "task":
                    if config["task"]: self.main = Task(self.data)
                    self.container.append(self.main)

                case _:
                    self.main = ElementError(self.data, "type")
                    self.container.append(self.main)
        except:
            self.main = ElementError(self.data, "parse")
        self.set_tooltip()

    def export(self):
        return self.main.save()

    def set_tooltip(self):
        try:
            if self.data["tooltip"]:
                self.set_tooltip_text(self.data["tooltip"])
        except KeyError:
            # No tooltip provided
            pass

    def create_controls(self):
        self.controls = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                halign=Gtk.Align.END,
                                valign=Gtk.Align.CENTER,
                                visible=False)
        self.up_btn = Gtk.Button(icon_name="go-up-symbolic")
        self.del_btn = Gtk.Button(icon_name="edit-delete-symbolic")
        self.down_btn = Gtk.Button(icon_name="go-down-symbolic")
        set_margins([self.up_btn, self.del_btn, self.down_btn], 1)
        self.controls.append(self.up_btn)
        self.controls.append(self.del_btn)
        self.controls.append(self.down_btn)

        if self.data["type"] == "body" and self.ai_config["enabled"]:
            print(f"Adding AI magic with {self.ai_config['model']}")
            self.ai_btn = Gtk.Button(icon_name="tool-magic-symbolic")
            set_margins(self.ai_btn, 1)
            self.controls.append(self.ai_btn)
            self.ai_container = AiConnector(self.ai_config["api_key"], self.ai_config["model"])
            self.ai_dialogue = AiGUI()
            self.ai_btn.connect("clicked", self.new_ai_dialogue)

        self.container.append(self.controls)
        set_margins(self.container, 10)

        self.append(self.container)

    def new_ai_dialogue(self, *args):
        self.ai_dialogue.present()
        print("gue")
        self.ai_container = AiGUI()


class Title(Gtk.Box):
    def __init__(self, data):
        super().__init__(margin_start=0)
        self.main = Gtk.Entry(text=data["text"],
                              css_name="title",
                              halign=Gtk.Align.START,
                              width_request=400,
                              height_request=10)
        self.append(self.main)

    def save(self):
        return {"type": "title", "text": self.main.get_text()}


class Body(Gtk.Box):
    def __init__(self, data):
        super().__init__(margin_start=5)
        self.main = Gtk.TextView(width_request=100, height_request=16,
                                 hexpand=True, css_classes=["list-item"],
                                 wrap_mode=Gtk.WrapMode.WORD)
        self.append(self.main)
        self.main.get_buffer().set_text((data["text"]))

    def save(self):
        return {"type": "body", "text": self.main.get_buffer().get_text(self.main.get_buffer().get_start_iter(),
                                                                        self.main.get_buffer().get_end_iter(),
                                                                        False)}


class Image(Gtk.Box):
    def __init__(self, data):
        super().__init__()
        if data["source"] == "url":
            print(f"Has scale {data['scale']}")
            self.data = data
            self.main = Gtk.Spinner(hexpand=True)
            self.append(self.main)
            self.main.start()
            process = threading.Thread(target=self.get_image_from_url)
            process.start()

        elif data["source"] == "file":
            self.main = Gtk.Image.new_from_file(data["file"])
            self.main.set_hexpand(True)
            self.main.set_vexpand(True)
            self.append(self.main)

    def get_image_from_url(self):
        try:
            response = requests.get(self.data["url"], allow_redirects=True)
            content = response.content
            loader = GdkPixbuf.PixbufLoader()
            loader.write_bytes(GLib.Bytes.new(content))
            loader.close()
            self.remove(self.main)
            self.main = Gtk.Image.new_from_pixbuf(loader.get_pixbuf())
            self.main.set_size_request((loader.get_pixbuf().get_width() / self.data["scale"]).__floor__(),
                                       (loader.get_pixbuf().get_height() / self.data["scale"]).__floor__())
            # self.main.set_hexpand(True)
            # self.main.set_vexpand(True)
        except requests.exceptions.ConnectionError:
            self.main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                hexpand=True)
            self.main.append(Gtk.Image(icon_name="auth-sim-missing-symbolic"))
            self.main.append(Gtk.Label(label="Unable to get image"))
        self.append(self.main)

    def save(self):
        return self.data  # Images can't be changed, so just return the original data


class List(Gtk.Box):
    def __init__(self, data):
        super().__init__(css_name="item-list", margin_start=5)
        self.children = []
        self.main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # self.main = Gtk.ListBox(css_name="item-list", selection_mode=Gtk.SelectionMode.NONE)
        for item in data["items"]:
            item = ListItem(item)
            item.main.connect("activate", self.add_item)
            self.main.append(item)
            item.main.grab_focus()
            self.children.append(item)
        self.append(self.main)

    def backspace_item(self, widget):
        self.main.remove(widget.get_parent())
        self.children.remove(widget.get_parent())

    def add_item(self, widget: Gtk.Entry):
        if widget.get_text():  # Prevents new tasks being added when last task is empty
            item = ListItem("")
            item.main.connect("activate", self.add_item)
            # item.main.connect("backspace", self.backspace_item)
            removed = []
            while True:
                next = self.main.get_last_child()
                if next == widget.get_parent():
                    item = ListItem()
                    self.children.insert(self.children.index(widget.get_parent()) + 1, item)
                    self.main.append(item)
                    for i in removed[::-1]:
                        self.main.append(i)
                    break
                else:
                    self.main.remove(next)
                    removed.append(next)
            item.main.grab_focus()
            self.children.append(item)

    def save(self):
        # Ensure that there aren't any empty items saved
        return {"type": "list", "items": [i.save() for i in self.children if i.save()]}


class ListItem(Gtk.Box):
    def __init__(self, text=""):
        super().__init__(css_name="item-list")
        self.append(Gtk.Label(label="•", css_name="bold_point"))
        self.main = Gtk.Entry(text=str(text),
                              width_request=400,
                              height_request=5,
                              css_name="list-item")
        self.append(self.main)

    def save(self):
        return self.main.get_text()


class Task(Gtk.Box):
    def __init__(self, data):
        super().__init__(css_name="item-list", margin_start=0)
        self.children = []
        self.main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # self.main = Gtk.ListBox(css_name="item-list", selection_mode=Gtk.SelectionMode.NONE)
        for item in data["items"]:
            if type(item) == list:
                self.add_item(task=item)
            else:
                print(f"Invalid task item {type(item)} rather than a list")
        self.append(self.main)

    def add_item(self, source=Gtk.Entry(text=" "), task=None):
        if task is None:
            task = ["", False]
        if source.get_text():  # Prevents new tasks being added when last task is empty
            item = TaskItem(task[0], task[1])
            item.main.connect("activate", self.add_item)
            self.main.append(item)
            item.main.grab_focus()
            self.children.append(item)

    def save(self):
        return {"type": "task", "items": [i.save() for i in self.children]}


class TaskItem(Gtk.Box):
    def __init__(self, text, status):
        super().__init__(css_name="item-list")
        self.check = Gtk.CheckButton()
        self.append(self.check)
        self.check.set_active(status)
        self.main = Gtk.Entry(text=str(text),
                              width_request=400,
                              height_request=5,
                              css_name="list-item")
        self.append(self.main)

    def save(self):
        return [self.main.get_text(), self.check.get_active()]


class ElementError(Gtk.Box):
    def __init__(self, data, error):
        super().__init__(margin_start=5)
        self.main = Gtk.Box()
        self.data = data
        self.main.append(Gtk.Image(icon_name="dialog-error-symbolic", margin_end=5))
        self.main.append(Gtk.Label(
            label=f"Unknown type '{self.data['type']}'" if error == "type"
            else "Unable to parse element data",
            halign=Gtk.Align.CENTER))

    def save(self):
        return self.data  # Broken elements are just saved as they were


def set_margins(widget, num):
    def margins(x, num):
        x.set_margin_start(num)
        x.set_margin_end(num)
        x.set_margin_top(num)
        x.set_margin_bottom(num)

    if type(widget) == list:
        for i in widget:
            margins(i, num)
    else:
        margins(widget, num)
