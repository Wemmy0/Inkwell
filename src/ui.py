from gi.repository import Gdk, Adw

from FileView import FileWindow
from ImageInsert import ImageDialogue
from NoteView import *

path = "Folder"


def log(*args):
    if verbose:
        print(*args)


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
        self.inserting_image = False  # Blocks the user from opening multiple image insert windows
        window.set_titlebar(self.header)

        main_container = Gtk.Paned()
        main_container.set_position(250)

        # Left pane
        # File viewer
        left_window = Gtk.ScrolledWindow()
        left_viewport = Gtk.Viewport()
        left_window.set_child(left_viewport)

        left_content = FileWindow(path, verbose)
        left_content.file_viewer.connect("row-activated", self.change_file)
        self.header.setup_new_note(left_content)
        left_viewport.set_child(left_content)

        main_container.set_start_child(left_window)

        # Right pane
        right_window = Gtk.ScrolledWindow()
        right_viewport = Gtk.Viewport()
        right_window.set_child(right_viewport)

        self.right_content = NoteView(self.header)
        right_viewport.set_child(self.right_content)

        main_container.set_end_child(right_window)

        window.set_child(main_container)

        self.header.save_btn.connect("clicked", self.right_content.save_file)
        self.header.edit_btn.connect("clicked", self.right_content.edit)
        self.header.new_image_btn.connect("clicked", self.new_image_dialogue)
        self.header.new_header_btn.connect("clicked", self.new_header)
        self.header.new_body_btn.connect("clicked", self.new_body)
        self.header.new_list_btn.connect("clicked", self.new_list)
        self.header.new_task_btn.connect("clicked", self.new_task)
        self.header.undo_btn.connect("clicked", self.right_content.undo)

    def change_file(self, file_viewer, row):
        # self.header.new_image_btn.show()
        # self.header.new_header_btn.show()
        # self.header.new_list_btn.show()
        # self.header.new_task_btn.show()
        # self.header.new_body_btn.show()
        self.header.new_btn.show()
        self.header.edit_btn.show()
        self.header.save_btn.show()
        self.header.info_btn.hide() # Hide the info button once a note is displayed to reduce clutter
        # self.header.undo_btn.show()
        file_path = file_viewer.files[file_viewer.file_rows.index(row)]
        self.right_content.change_file(file_path)

    def new_header(self, *args):
        self.header.new_popover.hide()
        self.right_content.add_element({"type": "title", "text": "Untitled"})

    def new_list(self, *args):
        self.header.new_popover.hide()
        self.right_content.add_element({"type": "list", "items": ["New List"]})

    def new_task(self, *args):
        self.header.new_popover.hide()
        self.right_content.add_element({"type": "task", "items": [["New Task", False]]})

    def new_body(self, *args):
        print("New Body")
        self.header.new_popover.hide()
        self.right_content.add_element({"type": "body", "text": "New Body Text"})

    def new_image_dialogue(self, *args):
        self.header.new_popover.hide()
        if not self.inserting_image:
            log("Opening image dialogue")
            dialogue = ImageDialogue()
            dialogue.present()
            self.inserting_image = True

            def get_insert_values(*args):
                data = dialogue.get_values()
                log("Inserting Image:", data)
                self.right_content.add_element(data)
                dialogue.close_window()
                self.inserting_image = False

            dialogue.insert_button.connect("clicked", get_insert_values)
        else:
            log("Image dialogue already open")


class HeaderUI(Gtk.HeaderBar):
    def __init__(self):
        super().__init__()
        self.set_show_title_buttons(True)

        self.info_btn = Gtk.Button(icon_name="dialog-information-symbolic",
                                   tooltip_text="About")
        self.pack_end(self.info_btn)
        about_dialogue = Adw.AboutWindow(application_name="Inkwell",
                                         application_icon="org.gnome.gedit-symbolic",
                                         version="1.2",
                                         license_type=Gtk.License.GPL_3_0,
                                         developer_name="Thomas Hoggarth",
                                         release_notes="<ul>"
                                                       "<li>Added undo button</li>"
                                                       "<li>Added styling to edit mode</li>"
                                                       "<li>Added body text element</li>"
                                                       "</ul>")

        def show_about_dialogue(*args):
            about_dialogue.present()

        self.info_btn.connect("clicked", show_about_dialogue)

        self.new_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.new_popover = Gtk.Popover(child=self.new_box)
        self.new_btn = Gtk.MenuButton(popover=self.new_popover,
                                      icon_name="tab-new-symbolic",
                                      visible=False)

        self.pack_end(self.new_btn)

        # New Note Button
        self.new_note_btn = Gtk.Button(icon_name="libreoffice-writer-symbolic",
                                       tooltip_text="New Note")
        self.pack_start(self.new_note_btn)

        # View mode button (Remove - not a priority)
        # self.view_mode_btn = Gtk.Button()
        # self.view_mode_btn.set_icon_name("org.gnome.gedit-symbolic")
        # self.view_mode_btn.set_tooltip_text("Switch to view mode")
        # self.view_mode_btn.connect("clicked", change_view_mode)
        # self.pack_end(self.view_mode_btn)

        # Edit Button
        self.edit_btn = Gtk.Button(icon_name="ymuse-edit-symbolic",
                                   visible=False)
        self.pack_end(self.edit_btn)

        # New Header Button
        self.new_header_btn = Gtk.Button(icon_name="format-text-larger-symbolic",
                                         tooltip_text="Insert Title")
        self.new_box.append(self.new_header_btn)

        # New Image Button
        self.new_image_btn = Gtk.Button(icon_name="image-x-generic-symbolic",
                                        tooltip_text="Insert Image")
        self.new_box.append(self.new_image_btn)

        # New List Button
        self.new_list_btn = Gtk.Button(icon_name="task-list-symbolic",
                                       tooltip_text="Insert List")
        self.new_box.append(self.new_list_btn)

        # New Task Button
        self.new_task_btn = Gtk.Button(icon_name="checkbox-checked-symbolic",
                                       tooltip_text="Insert Task")
        self.new_box.append(self.new_task_btn)

        # New Body Button
        self.new_body_btn = Gtk.Button(icon_name="tool-text-symbolic",
                                       tooltip_text="Insert Body Text")
        self.new_box.append(self.new_body_btn)

        # Save Button
        self.save_btn = Gtk.Button(icon_name="document-save-symbolic",
                                   visible=False)
        self.pack_end(self.save_btn)

        self.undo_btn = Gtk.Button(icon_name="edit-undo-symbolic",
                                   visible=False)
        self.pack_end(self.undo_btn)

    def setup_new_note(self, file_viewer):
        self.new_note_btn.connect("clicked", file_viewer.add_note)


def set_margins(widget, num):
    widget.set_margin_start(num)
    widget.set_margin_end(num)
    widget.set_margin_top(num)
    widget.set_margin_bottom(num)
