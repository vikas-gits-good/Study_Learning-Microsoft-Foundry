import os

base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "exe.js")

with open(file_path, "r", encoding="utf-8") as f:
    dom_js = f.read()

print(dom_js)
