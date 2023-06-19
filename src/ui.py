from gi.repository import Gdk

from FileView import FileWindow
from ImageInsert import ImageDialogue
from NoteView import *

path = "Folder"


def log(*args):
    if verbose:
        print(*args)


# class Text:
#     def __init__(self):
#         self.text_content = ""
#         self.pane = Gtk.ScrolledWindow()
#
#         self.viewport = Gtk.Viewport()
#         self.pane.set_child(self.viewport)
#         self.text = Gtk.TextView()
#         self.viewport.set_child(self.text)
#         self.buffer = self.text.get_buffer()

# Removed, sync only on app open/close
# self.text.connect("backspace", self.detect_changes)
# self.text.connect("delete-from-cursor", self.detect_changes)

# def detect_changes(self, widget):
#     self.text_content = self.buffer.get_text(self.buffer.get_start_iter(),
#                                              self.buffer.get_end_iter(), False)
#     log("Changes detected")


class UI:
    def __init__(self, window, debug):
        global verbose
        verbose = debug
        log("Building UI...")

        # Custom CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('./src/style.css')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.header = HeaderUI()
        window.set_titlebar(self.header)

        main_container = Gtk.Paned()
        main_container.set_position(250)

        # Left pane
        # File viewer
        left_window = Gtk.ScrolledWindow()
        left_viewport = Gtk.Viewport()
        left_window.set_child(left_viewport)

        left_content = FileWindow(path, verbose, [self.header.new_note_btn, self.header.new_task_btn])
        left_content.file_viewer.connect("row-activated", self.change_file)
        self.header.setup_new_note(left_content)
        left_viewport.set_child(left_content)

        main_container.set_start_child(left_window)

        # Right pane
        right_window = Gtk.ScrolledWindow()
        right_viewport = Gtk.Viewport()
        right_window.set_child(right_viewport)

        self.right_content = NoteView()
        right_viewport.set_child(self.right_content)
        self.header.ImageDialogue.insert_button.connect("clicked", self.insert_image)

        main_container.set_end_child(right_window)

        window.set_child(main_container)

        self.header.save_btn.connect("clicked", self.right_content.save_file)

    def change_file(self, file_viewer, row):
        file_path = file_viewer.files[file_viewer.file_rows.index(row)]
        self.right_content.change_file(file_path)

    def insert_image(self, *args):
        data = self.header.ImageDialogue.get_values()
        log("Inserting Image:", data)
        self.right_content.add_element(data)
        self.header.ImageDialogue.close()


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
        # TODO: Create new tasks

        # # View mode button (Remove - not a priority)
        # self.view_mode_btn = Gtk.Button()
        # self.view_mode_btn.set_icon_name("org.gnome.gedit-symbolic")
        # self.view_mode_btn.set_tooltip_text("Switch to view mode")
        # self.view_mode_btn.connect("clicked", change_view_mode)
        # self.pack_end(self.view_mode_btn)

        # region Menu
        self.menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic")
        self.pack_end(self.menu_btn)
        # endregion

        # New Header Button
        self.new_header_btn = Gtk.Button(icon_name="format-text-larger-symbolic",
                                         tooltip_text="Insert Title")
        self.pack_end(self.new_header_btn)

        # New Image Button
        self.new_image_btn = Gtk.Button(icon_name="image-x-generic-symbolic",
                                        tooltip_text="Insert Image")
        self.pack_end(self.new_image_btn)
        self.new_image_btn.connect('clicked', self.new_image_dialogue)
        self.ImageDialogue = ImageDialogue()

        # region Save Button
        self.save_btn = Gtk.Button(label="Save")
        self.pack_end(self.save_btn)
        # endregion

    def new_image_dialogue(self, *args):
        self.ImageDialogue.present()
        # self.ImageDialogue = ImageDialogue()
        # self.ImageDialogue.insert_button.connect("clicked", self.insert_from_dialogue)

    def setup_new_note(self, file_viewer):
        self.new_note_btn.connect("clicked", file_viewer.add_note)


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
