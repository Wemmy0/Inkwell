from NoteView import Title, Body, Image, List, Task, ElementError
from gi.repository import Gtk


def export_to_markdown(content: list, path: str):
    # Purpose: Given list of elements, export them to a markdown file
    result = []
    broken = 0
    for element in content:
        if type(element.main) is Body:
            result.append(element.main.save()["text"])
        elif type(element.main) is Title:
            result.append(f"### {element.main.save()['text']}")
        elif type(element.main) is List:
            result += [f"- {item}" for item in element.main.save()["items"]]
        elif type(element.main) is Task:
            result += [f"- [{'x' if item[1] else ' '}] {item[0]}" for item in element.main.save()["items"]]
        elif type(element.main) is Image:
            data = element.main.save()
            try:
                if data["source"] == "url":
                    result += [f"![{data['tooltip']}]({data['url']})"]
                elif data["source"] == "file":
                    result += [f"![{data['tooltip']}]({data['file'][data['file'].find("/") + 1:]})"]
                else:
                    broken += 1
            except KeyError:
                broken += 1
        elif type(element.main) is ElementError:
            broken += 1

    finalise(result, path, broken)


def finalise(data: list, path: str, err: int):
    # Purpose: Given a list of the content of every element,
    # try and save the file to disk with each item being a new line
    try:
        with open(path[:path.rfind('.')] + ".md", "w+") as file:
            for line in data:
                file.write(line + "\n")
        dialogue = Gtk.MessageDialog(text="File Successfully Exported",
                                     secondary_text=path[:path.rfind('.')] + ".md" + (f"\n{err} elements where skipped"
                                                                                      if err else ""),
                                     message_type=Gtk.MessageType.INFO,
                                     buttons=Gtk.ButtonsType.OK)
    except:
        dialogue = Gtk.MessageDialog(text="Unable to export file",
                                     message_type=Gtk.MessageType.INFO,
                                     buttons=Gtk.ButtonsType.OK)
    finally:
        dialogue.connect("response", lambda dialog, *args: dialog.destroy())
        dialogue.present()
