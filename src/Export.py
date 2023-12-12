from NoteView import Title, Body, Image, List, Task
from gi.repository import Gtk


def export_to_markdown(content, path):
    # Purpose: Given list of elements, export them to a markdown file
    result = []
    for element in content:
        # TODO: Export images
        if type(element.main) is Body:
            result.append(element.main.save()["text"])
        elif type(element.main) is Title:
            result.append(f"### {element.main.save()['text']}")
        elif type(element.main) is List:
            result += [f"- {item}" for item in element.main.save()["items"]]
        elif type(element.main) is Task:
            result += [f"- [{'x' if item[1] else ' '}] {item[0]}" for item in element.main.save()["items"]]
    finalise(result, path)


def finalise(data, path):
    # Purpose: Given a list of the content of every element,
    # try and save the file to disk with each item being a new line
    try:
        with open(path[:path.rfind('.')] + ".md", "w+") as file:
            for line in data:
                file.write(line + "\n")
        dialogue = Gtk.MessageDialog(text="File Successfully Exported",
                                     secondary_text=path[:path.rfind('.')] + ".md",
                                     message_type=Gtk.MessageType.INFO,
                                     buttons=Gtk.ButtonsType.OK)
    except:
        dialogue = Gtk.MessageDialog(text="Unable to export file",
                                     message_type=Gtk.MessageType.INFO,
                                     buttons=Gtk.ButtonsType.OK)
    dialogue.connect("response", lambda dialog, *args: dialog.destroy())
    dialogue.present()
