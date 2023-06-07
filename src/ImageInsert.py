from gi.repository import Gtk, Adw


class ImageDialogue(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_title("Insert Image")

        self.page = Adw.PreferencesPage()
        self.set_child(self.page)

        self.group = Adw.PreferencesGroup(description="Insert a new image into your note")
        self.page.add(self.group)

        # region source
        self.select_source_row = Adw.ActionRow(title="Select Image Source",
                                               subtitle="Please choose where the image is located")
        self.source_dropdown = Gtk.ComboBoxText(valign=Gtk.Align.CENTER)

        sources = ["Local File", "URL", "Wikimedia", "Web Embed"]
        for source in sources:
            self.source_dropdown.append_text(source)

        self.source_dropdown.connect('changed', self.select_source)
        self.select_source_row.add_suffix(self.source_dropdown)
        self.group.add(self.select_source_row)
        # endregion

        # region URL Entry
        self.url_row = Adw.ActionRow(title="URL of the file",
                                     visible=False)
        self.url_entry = Gtk.Entry(placeholder_text="http://example.com/image.png",
                                   valign=Gtk.Align.CENTER)
        self.url_row.add_suffix(self.url_entry)
        self.group.add(self.url_row)
        # endregion

        # region File Entry
        self.file_row = Adw.ActionRow(title="Name of image file",
                                      subtitle="Image must be in notes folder",
                                      visible=False)
        # TODO: Make this open file selector
        self.file_entry = Gtk.Entry(placeholder_text="Image.png",
                                    valign=Gtk.Align.CENTER)
        self.file_row.add_suffix(self.file_entry)
        self.group.add(self.file_row)
        # endregion

        # region Wikimedia Query Entry
        self.wikimedia_row = Adw.ActionRow(title="Image search query",
                                           visible=False)
        self.wikimedia_entry = Gtk.Entry(placeholder_text="President Obama",
                                         valign=Gtk.Align.CENTER)
        self.wikimedia_row.add_suffix(self.wikimedia_entry)
        self.group.add(self.wikimedia_row)

        # endregion

        # region Web Embed Entry
        self.web_embed_row = Adw.ActionRow(title="URL of the page",
                                           visible=False)
        self.web_embed_entry = Gtk.Entry(placeholder_text="http://example.com/",
                                         valign=Gtk.Align.CENTER)
        self.web_embed_row.add_suffix(self.web_embed_entry)
        self.group.add(self.web_embed_row)
        # endregion

        # region Cache to local file
        self.cache_image_row = Adw.ActionRow(title="Cache to file",
                                             subtitle="Download the file to notes folder for offline viewing",
                                             visible=False)
        self.cache_image_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.cache_image_row.add_suffix(self.cache_image_switch)
        self.group.add(self.cache_image_row)
        # endregion

        # region image preview
        self.image_preview_row = Adw.ActionRow(visible=False)
        self.group.add(self.image_preview_row)
        # endregion

        # Change source to the local file as default
        self.source_dropdown.set_active(0)
        self.change_source("Local File")

        # Header UI
        self.header = Gtk.HeaderBar(show_title_buttons=False)
        self.insert_button = Gtk.Button(label="Insert")
        self.insert_button.add_css_class("suggested-action")
        self.header.pack_end(self.insert_button)

        self.cancel_button = Gtk.Button(label="Cancel")
        self.cancel_button.connect('clicked', self.close_window)
        self.header.pack_start(self.cancel_button)

        self.set_titlebar(self.header)
        self.set_default_size(500, 600)

    def change_source(self, text):
        self.url_row.hide()
        self.file_row.hide()
        self.wikimedia_row.hide()
        self.web_embed_row.hide()
        self.cache_image_row.hide()
        # self.url_entry.set_text()
        match text:
            case "Local File":
                self.file_row.show()
            case "URL":
                self.url_row.show()
                self.cache_image_row.show()
                # self.url_entry.connect("")
            case "Wikimedia":
                self.wikimedia_row.show()
                self.cache_image_row.show()
            case "Web Embed":
                self.web_embed_row.show()

    # def preview_url(self):


    def close_window(self, *args):
        self.close()

    def select_source(self, *args):
        self.change_source(self.source_dropdown.get_active_text())
