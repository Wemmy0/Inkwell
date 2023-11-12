from NoteView import Title, Body, Image, List, Task


def export_to_markdown(content):
    result = []
    for element in content:
        if type(element.main) is Body:
            result.append(element.main.save()["text"])
        elif type(element.main) is Title:
            result.append(f"### {element.main.save()['text']}")
        elif type(element.main) is List:
            result += element.main.save()["items"]
        elif type(element.main) is Task:
            result += [f"- [{'x' if item[1] else ' '}] {item[0]}" for item in element.main.save()["items"]]
    finalise(result)


def finalise(data):
    print(data)
