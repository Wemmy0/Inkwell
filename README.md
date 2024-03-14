# Inkwell
![](Assets/UI.png)
<p align="center"><img src="https://github.com/Wemmy0/Inkwell/actions/workflows/pylint.yml/badge.svg" /></p>

A minimalistic rich text notes app written in GTK4 and Python

### Running from source (Fedora):
1. Clone repository using git:
```
git clone https://github.com/Wemmy0/Inkwell/
```

2. Create new venv & activate it
```
python -m venv ./venv
source ./venv/bin/activate
```

3. Install the required dependancies
```
dnf install gobject-introspection-devel
pip install PyGObject mysql-connector-python openai pycairo requests
```

 4. Start Inkwell
```
python src/main.py
```
