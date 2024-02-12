from gi.repository import Gtk
from gi.repository import Adw  # pylint: disable=no-name-in-module


class ImageDialogue(Gtk.Window):
    def __init__(self, url_source, file_source, wikimedia_source, web_source, cache_support):
        super().__init__()
        self.cache_support = cache_support
        self.set_title("Insert Image")

        self.page = Adw.PreferencesPage()
        self.set_child(self.page)

        self.group = Adw.PreferencesGroup(description="Insert a new image into your note")
        self.page.add(self.group)

        # region source
        self.select_source_row = Adw.ActionRow(title="Select Image Source",
                                               subtitle="Please choose where the image is located")
        self.source_dropdown = Gtk.ComboBoxText(valign=Gtk.Align.CENTER)

        if url_source: self.source_dropdown.append_text("URL")
        if file_source: self.source_dropdown.append_text("Local File")
        if wikimedia_source: self.source_dropdown.append_text("Wikimedia")
        if web_source: self.source_dropdown.append_text("Web Embed")

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
        self.wikipedia_row = Adw.ActionRow(title="Image search query",
                                           visible=False)
        self.wikimedia_entry = Gtk.Entry(placeholder_text="President Obama",
                                         valign=Gtk.Align.CENTER)
        self.wikipedia_row.add_suffix(self.wikimedia_entry)
        self.group.add(self.wikipedia_row)

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
        # TODO: Actually do this
        if cache_support:
            self.cache_image_row = Adw.ActionRow(title="Cache to file",
                                                 subtitle="Download the file to notes folder for offline viewing",
                                                 visible=False)
            self.cache_image_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
            self.cache_image_row.add_suffix(self.cache_image_switch)
            self.group.add(self.cache_image_row)
        # endregion

        # region Scale slider
        self.scale_row = Adw.ActionRow(visible=False)
        self.scale_slider = Gtk.Scale(round_digits=1)
        self.scale_slider.set_range(0, 1.5)
        self.scale_slider.set_digits(True)
        for i in range(0, 15):
            self.scale_slider.add_mark(i/10, Gtk.PositionType.BOTTOM)
        # self.scale_slider.add_mark(1, Gtk.PositionType.BOTTOM)
        # # self.scale_slider = Gtk.Range()
        # self.scale_row.add_suffix(self.scale_slider)
        self.group.add(self.scale_slider)

        # region Tooltip
        self.tooltip_row = Adw.ActionRow(title="Description",
                                         subtitle="Shown when hovering over the element")
        self.tooltip_entry = Gtk.Entry(valign=Gtk.Align.CENTER)
        self.tooltip_row.add_suffix(self.tooltip_entry)
        self.group.add(self.tooltip_row)
        # endregion

        # region image preview
        # self.image_preview_row = Adw.ActionRow(visible=False)
        # self.group.add(self.image_preview_row)
        # endregion

        # Change source to the local file as default
        self.source_dropdown.set_active(0)
        self.change_source("URL")

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
        self.wikipedia_row.hide()
        self.web_embed_row.hide()
        self.scale_slider.hide()
        if self.cache_support:
            self.cache_image_row.hide()
        self.tooltip_row.show()
        match text:
            case "URL":
                self.url_row.show()
                if self.cache_support:
                    self.cache_image_row.show()
                    self.scale_slider.show()
            case "Local File":
                self.file_row.show()
            case "Wikipedia":
                self.wikipedia_row.show()
                if self.cache_support:
                    self.cache_image_row.show()
            case "Web Embed":
                self.web_embed_row.show()
                self.tooltip_row.hide()

    def close_window(self, *args):
        print("Closing image dialogue")
        self.close()

    def select_source(self, *args):
        self.change_source(self.source_dropdown.get_active_text())

    def get_values(self):
        if self.source_dropdown.get_active_text() == "Wikipedia":
            pass

        source_dropdown = self.source_dropdown.get_active_text()
        url = self.url_entry.get_text()
        file = self.file_entry.get_text()
        tooltip = self.tooltip_entry.get_text()
        scale = self.scale_slider.get_value()
        # cache = self.cache_image_switch.get_state()
        sources = {"URL": "url", "Local File": "file", "Wikipedia": "wikimedia"}
        data = {"type": "image" if source_dropdown != "Web Embed" else "iframe",
                "source": sources[source_dropdown],
                "url": url,
                "file": file,
                "scale": scale,
                "tooltip": tooltip}
                # "cache": cache}
        return data
