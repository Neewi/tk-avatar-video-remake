"""Build a portable, offline gallery from the approved avatar catalog."""
import json
import hashlib
import os
from pathlib import Path
from urllib.parse import quote


def render_gallery(project, people):
    output = project / "Avatar Studio.html"
    rows = []
    for person in people:
        looks = []
        for look in person["looks"]:
            views = {
                key: quote(Path(path).relative_to(project).as_posix(), safe="/")
                + "?v=" + hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]
                for key, path in look["views"].items()
            }
            looks.append(dict(look, views=views))
        rows.append(dict(person, looks=looks))
    # Keep user-authored names/descriptions inside the JSON script element.
    payload = json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c")
    template = Path(__file__).with_name("gallery.html").read_text(encoding="utf-8")
    content = template.replace("__AVATAR_CATALOG__", payload)
    if not output.exists() or output.read_text(encoding="utf-8") != content:
        temporary = output.with_suffix(".html.tmp")
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, output)
    return str(output)
