from gi.repository import Gtk
import os
from os.path import isfile


def log(*args):
	if verbose:
		print(*args)


class FileViewer(Gtk.ListBox):
	def __init__(self, path):
		super().__init__()
		self.detect_changes(path)

	def detect_changes(self, path):
		files = self._scan_files(path)
		self._update_files(files)

	def _scan_files(self, path):
		out = []
		for i in os.listdir(path):
			if not isfile(path + "/" + i):
				out = out + self._scan_files(path + "/" + i)
			else:
				log(f"Found file {path + '/' + i}")
				out.append(path + "/" + i)
		return out

	def _update_files(self, files):
		for i in files:
			self.append(Gtk.Label(label = i))


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

	main_container = Gtk.Paned()

	# Left pane
	left_pane = Gtk.ScrolledWindow()
	left_viewport = Gtk.Viewport()
	left_pane.set_child(left_viewport)

	file_view = FileViewer("Folder")
	left_viewport.set_child(file_view)

	main_container.set_start_child(left_pane)

	# Right pane
	right = Text()
	main_container.set_end_child(right.pane)

	window.set_child(main_container)


def save_text(text):
	print("Saving...")
	print(text.get_buffer().get_text(text.get_buffer().get_start_iter(), text.get_buffer().get_end_iter(), False))


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
