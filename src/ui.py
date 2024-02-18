from gi.repository import Gtk, Gdk
from gi.repository import Adw  # pylint: disable=no-name-in-module

from FileView import FileWindow
from ImageInsert import ImageDialogue
from NoteView import *
from Export import *


def log(*args):
    if verbose:
        print(*args)


class UI:
    def __init__(self, window, config, debug):
        global verbose
        verbose = debug
        self.config = config
        log("Building UI...")

        # Custom CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('./src/style.css')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.header = HeaderUI(self.config)
        self.inserting_image = False  # Blocks the user from opening multiple image insert windows
        window.set_titlebar(self.header)

        main_container = Gtk.Paned()
        main_container.set_position(250)

        # Left pane - File Viewer
        left_window = Gtk.ScrolledWindow()
        left_viewport = Gtk.Viewport()
        left_window.set_child(left_viewport)

        left_content = FileWindow(self.config["path"], self.config["colour-support"], verbose)
        left_content.file_viewer.connect("row-activated", self.change_file)
        self.header.setup_new_note(left_content)
        left_viewport.set_child(left_content)

        main_container.set_start_child(left_window)

        # Right pane - Note View
        right_window = Gtk.ScrolledWindow()
        right_viewport = Gtk.Viewport()
        right_window.set_child(right_viewport)

        self.right_content = NoteView(self.config["elements"], self.config["AI-Configuration"],
                                      self.config["read-only"], self.header)
        right_viewport.set_child(self.right_content)

        main_container.set_end_child(right_window)

        window.set_child(main_container)

        elements = self.config["elements"]
        self.header.save_btn.connect("clicked", self.right_content.save_file)
        self.header.edit_btn.connect("clicked", self.right_content.edit)
        if elements["image"]: self.header.new_image_btn.connect("clicked", self.new_image_dialogue)
        if elements["title"]: self.header.new_header_btn.connect("clicked", self.new_header)
        if elements["body"]: self.header.new_body_btn.connect("clicked", self.new_body)
        if elements["list"]: self.header.new_list_btn.connect("clicked", self.new_list)
        if elements["task"]: self.header.new_task_btn.connect("clicked", self.new_task)
        self.header.undo_btn.connect("clicked", self.right_content.undo)
        self.header.export_btn.connect("clicked", self.export)

    def export(self, *args):
        print("Exporting")
        export_to_markdown(self.right_content.children, self.right_content.filename)

    def change_file(self, file_viewer, row):
        # Purpose: Show button elements and trigger the change_file function of the note viewer
        if not self.config["read-only"]:
            self.header.new_btn.show()
            self.header.edit_btn.show()
            self.header.save_btn.show()
            self.header.export_btn.show()
        self.header.info_btn.hide()  # Hide the info button once a note is displayed to reduce clutter
        file_path = file_viewer.files[file_viewer.file_rows.index(row)]
        self.right_content.change_file(file_path)

    def new_header(self, *args):
        # Purpose: Add new header element
        self.header.new_popover.hide()
        self.right_content.add_element({"type": "title", "text": "Untitled"})

    def new_list(self, *args):
        # Purpose: Add new list element
        self.header.new_popover.hide()
        self.right_content.add_element({"type": "list", "items": ["New List"]})

    def new_task(self, *args):
        # Purpose: Add new task element
        self.header.new_popover.hide()
        self.right_content.add_element({"type": "task", "items": [["New Task", False]]})

    def new_body(self, *args):
        # Purpose: Add new body element
        self.header.new_popover.hide()
        self.right_content.add_element({"type": "body", "text": "New Body Text"})

    def new_image_dialogue(self, *args):
        # Purpose: Create new image dialogue, getting values when "Insert" button is pressed
        self.header.new_popover.hide()
        if not self.inserting_image:
            log("Opening image dialogue")
            sources = self.config["image-configuration"]
            dialogue = ImageDialogue(sources["url_source"], sources["file_source"], sources["wikimedia_source"],
                                     sources["web_source"], sources["cache_support"])
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
    def __init__(self, config):
        super().__init__()
        self.set_show_title_buttons(True)
        self.info_btn = Gtk.Button(icon_name="dialog-information-symbolic",
                                   tooltip_text="About")
        self.pack_end(self.info_btn)
        about_dialogue = Adw.AboutWindow(application_name="Inkwell",
                                         application_icon="org.gnome.gedit-symbolic",
                                         version="1.3.5",
                                         license_type=Gtk.License.GPL_3_0,
                                         developer_name="Thomas Hoggarth",
                                         release_notes="<p>This changelog maybe out of date. Please see: https://github.com/Wemmy0/Inkwell/commits/main</p>"
                                                       "<p>1.3.5:</p>"
                                                       "<ul>"
                                                       "<li>Invalid colours will default to the first found colour</li>"
                                                       "</ul>"
                                                       "<p>1.3:</p>"
                                                       "<ul>"
                                                       "<li>Added configuration.toml file</li>"
                                                       "<li>Fixed highlighting of task/list items</li>"
                                                       "<li>Sync, Elements, AI and more can be enabled/disabled in the config file</li>"
                                                       "<li>Fixed a crash when sync connection was invalid but was attempted to be closed anyway</li>"
                                                       "<li>Colours can be added/removed from the Assets/ folder</li>"
                                                       "</ul>"
                                                       "<p>1.2:</p>"
                                                       "<ul>"
                                                       "<li>Added undo button</li>"
                                                       "<li>Added undo button</li>"
                                                       "<li>Added styling to edit mode</li>"
                                                       "<li>Added body text element</li>"
                                                       "</ul>")

        def show_about_dialogue(*args):
            about_dialogue.present()

        self.info_btn.connect("clicked", show_about_dialogue)

        if config["read-only"]:
            self.pack_end(Gtk.Label(label="Read-Only Mode"))

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

        # Edit Button
        self.edit_btn = Gtk.Button(icon_name="ymuse-edit-symbolic",
                                   visible=False)
        self.pack_end(self.edit_btn)

        # New Header Button
        elements = config["elements"]
        if elements["title"]:
            self.new_header_btn = Gtk.Button(icon_name="format-text-larger-symbolic",
                                             tooltip_text="Insert Title")
            self.new_box.append(self.new_header_btn)

        # New Image Button
        if elements["image"]:
            self.new_image_btn = Gtk.Button(icon_name="image-x-generic-symbolic",
                                            tooltip_text="Insert Image")
            self.new_box.append(self.new_image_btn)

        # New List Button
        if elements["list"]:
            self.new_list_btn = Gtk.Button(icon_name="task-list-symbolic",
                                           tooltip_text="Insert List")
            self.new_box.append(self.new_list_btn)

        # New Task Button
        if elements["task"]:
            self.new_task_btn = Gtk.Button(icon_name="checkbox-checked-symbolic",
                                           tooltip_text="Insert Task")
            self.new_box.append(self.new_task_btn)

        # New Body Button
        if elements["body"]:
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

        # Export Button
        self.export_btn = Gtk.Button(icon_name="document-export-symbolic",
                                     visible=False)
        self.pack_end(self.export_btn)

    def setup_new_note(self, file_viewer):
        self.new_note_btn.connect("clicked", file_viewer.add_note)
