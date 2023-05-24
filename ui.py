from gi.repository import Gtk, Gdk
import json
import os
from os.path import isfile


def log(*args):
	if verbose:
		print(*args)


def initialise_json(filename):
	# If json file isn't found, create it with json {}
	with open(filename, "w+") as file:
		file.write("{}")


class FileViewer(Gtk.ListBox):
	def __init__(self, path):
		super().__init__()
		self.path = path
		self.blacklist = [path + "/" + "colours.json"]

		self.palette = os.listdir("Assets")
		self.files = self.scan_files(path)
		self.initialise_colours()
		self.add_files(self.files)
		self.connect("row-selected", self.row_clicked)

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
			if i not in self.blacklist:
				self.append(FileViewRow(i, self.palette, self.json_data))

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

	def row_clicked(self, container, row):
		print(f"Clicked row {row.get_index()}")


class FileViewRow(Gtk.Box):
	def __init__(self, filename, palette, current_colours):
		self.filename = filename
		super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
		self.palette = palette
		self.popover = Gtk.Popover()

		# Image containing circle, popout to selector of colour
		self.image = Gtk.Image()
		self.current_colours = current_colours
		self.current_colour = "Assets/" + current_colours[self.filename]
		self.image.set_from_file(self.current_colour)
		self.colour_popover()

		# TODO: Remove border of button - it's very ugly
		colour_button = Gtk.MenuButton(child=self.image)
		colour_button.set_popover(self.popover)
		self.append(colour_button)

		# Box containing file name on the top and start of contents at the button
		right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		filename_label = Gtk.Label(label=self.filename)
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
		print(self.palette.index(self.current_colour.replace("Assets/", "")))

		for i in self.palette:
			container.append(Gtk.Image(file="Assets/" + i))

		container.select_row(container.get_row_at_index(self.palette.index(self.current_colour.replace("Assets/", ""))))
		container.connect("row-selected", self.change_colour)

		self.popover.set_child(container)

	def change_colour(self, container, row):
		self.image.set_from_file("Assets/" + self.palette[row.get_index()])
		self.current_colours[self.filename] = self.palette[row.get_index()]

		# TODO: This should use path provided instead of hard-coded
		with open("Folder/colours.json", "w") as file:
			json.dump(self.current_colours, file)


class Text:
	def __init__(self):
		self.text_content = ""
		self.pane = Gtk.ScrolledWindow()

		self.viewport = Gtk.Viewport()
		self.pane.set_child(self.viewport)
		self.text = Gtk.TextView()
		self.viewport.set_child(self.text)
		self.buffer = self.text.get_buffer()

		self.text.connect("backspace", self.detect_changes)
		self.text.connect("delete-from-cursor", self.detect_changes)

	def detect_changes(self, widget):
		self.text_content = self.buffer.get_text(self.buffer.get_start_iter(),
		                                         self.buffer.get_end_iter(), False)
		log("Changes detected")


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

	create_header_ui(window)

	main_container = Gtk.Paned()
	main_container.set_position(200)

	# Left pane
	left_pane = Gtk.ScrolledWindow()
	left_viewport = Gtk.Viewport()
	left_viewport.set_hadjustment()
	left_pane.set_child(left_viewport)

	file_view = FileViewer("Folder")
	left_viewport.set_child(file_view)

	main_container.set_start_child(left_pane)

	# Right pane
	right = Text()
	main_container.set_end_child(right.pane)

	window.set_child(main_container)


def create_header_ui(window):
	# Header UI
	header = Gtk.HeaderBar()
	header.set_show_title_buttons(True)
	window.set_titlebar(header)
	# New Note Button
	new_note_btn = Gtk.Button()
	new_note_btn.set_icon_name("libreoffice-writer-symbolic")
	new_note_btn.set_tooltip_text("checkbox-checked-symbolic")
	header.pack_start(new_note_btn)
	# New Task Button
	new_task_btn = Gtk.Button()
	new_task_btn.set_icon_name("checkbox-checked-symbolic")
	new_task_btn.set_tooltip_text("checkbox-checked-symbolic")
	header.pack_start(new_task_btn)
	# View mode button
	view_mode_btn = Gtk.Button()
	view_mode_btn.set_icon_name("org.gnome.gedit-symbolic")
	view_mode_btn.set_tooltip_text("Editing Mode")
	view_mode_btn.connect("clicked", change_view_mode)
	header.pack_end(view_mode_btn)


def change_view_mode(button):
	current_mode = button.get_icon_name()
	match current_mode:
		case "org.gnome.gedit-symbolic":
			# Toggle to view mode
			print("Switching to view mode")
			button.set_icon_name("ephy-reader-mode-symbolic")
		case "ephy-reader-mode-symbolic":
			# Toggle to edit mode
			print("Switching to edit mode")
			button.set_icon_name("org.gnome.gedit-symbolic")
