"""List usable looks and product previews, or publish a complete approved look."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid

from PIL import Image


def project_paths(explicit=None):
    """Locate the shared project from an explicit path, current directory or skill."""
    override = explicit or os.environ.get("AVATAR_REMAKE_PROJECT")
    if override:
        candidates = [Path(override).expanduser().resolve()]
    else:
        cwd = Path.cwd().resolve()
        installed = Path(__file__).resolve().parent
        candidates = [cwd, *cwd.parents, installed, *installed.parents]
    for root in candidates:
        marker = root / "avatar-remake.json"
        if marker.is_file():
            config = json.loads(marker.read_text(encoding="utf-8"))
            return root, root / config["studio"], root / config["products"]
    raise ValueError("请在 TK数字人视频 项目中运行，或使用 --project 指定包含 avatar-remake.json 的项目目录。")


VIEWS = ("portrait", "three-quarter", "full-front", "full-back")


def directories(parent):
    if not parent.exists():
        return []
    return sorted(p for p in parent.iterdir() if p.is_dir() and not p.name.startswith("."))


def catalog(root):
    people = []
    for person in directories(root / "people"):
        looks = []
        for look in directories(person / "looks"):
            if not (look / "look.json").is_file():
                continue
            record = json.loads((look / "look.json").read_text(encoding="utf-8"))
            views = {key: str(look / (key + ".png")) for key in VIEWS}
            if not all(Path(path).is_file() for path in views.values()):
                raise ValueError(f"造型图不完整，请检查 {look}")
            looks.append(dict(record, views=views))
        if looks:
            looks.sort(key=lambda look: (not look.get("original", False), look["name"]))
            people.append(dict(id=person.name, name=looks[0]["person"], looks=looks))
    return people


def products(root):
    if not root.is_dir():
        raise ValueError(f"找不到产品素材目录 {root}")
    result = []
    for folder in directories(root):
        if folder.name == "配件":
            continue
        for file in ("hero-clean.png", "front-clean.png", "flat-lay-clean.png"):
            preview = folder / file
            if preview.is_file():
                result.append(dict(sku=folder.name, preview=str(preview), folder=str(folder)))
                break
    return sorted(result, key=lambda row: (row["sku"] != "T10P", row["sku"]))


def save(root, args):
    people = catalog(root)
    name = args.look.strip()
    if not name or not args.description.strip() or (args.new_person is not None and not args.identity.strip()):
        raise ValueError("请填写造型名称、造型描述和人物外观。")
    new = args.new_person is not None
    if new:
        person_name = args.new_person.strip()
        if not person_name or any(p["name"] == person_name for p in people):
            raise ValueError("请使用一个尚未使用的人物名称。")
        person_id = uuid.uuid4().hex
        identity = args.identity.strip()
    else:
        person = next((p for p in people if p["id"] == args.person_id), None)
        if person is None:
            raise ValueError("请从人物库选择有效的人物编号。")
        if any(look["name"] == name for look in person["looks"]):
            raise ValueError("该人物已经有同名造型，请另取造型名。")
        person_id, person_name = person["id"], person["name"]
        identity = person["looks"][0]["identity"]

    # Prepare on the same volume. Readers only see complete, renamed directories.
    target = root / "people" / person_id / "looks"
    look_id = uuid.uuid4().hex
    with tempfile.TemporaryDirectory(dir=root, prefix=".pending-") as work:
        stage = Path(work) / "look"
        stage.mkdir()
        for key in VIEWS:
            with Image.open(args.images / (key + ".png")) as img:
                img.load()
                if img.format != "PNG":
                    raise ValueError(f"{key}.png 需要是真实 PNG 图片。")
            shutil.copyfile(args.images / (key + ".png"), stage / (key + ".png"))
        record = dict(id=look_id, person=person_name, name=name,
                      identity=identity, original=new, description=args.description.strip())
        (stage / "look.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        target.mkdir(parents=True, exist_ok=True)
        stage.rename(target / look_id)
    return dict(person_id=person_id, look_id=look_id, folder=str(target / look_id))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, help="共享项目根目录")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("people")
    commands.add_parser("products")
    publish = commands.add_parser("save-look")
    group = publish.add_mutually_exclusive_group(required=True)
    group.add_argument("--new-person")
    group.add_argument("--person-id")
    publish.add_argument("--look", required=True)
    publish.add_argument("--identity", default="", help="新建人物时填写固定外观，换装时继承")
    publish.add_argument("--description", required=True, help="发型、服装等造型细节")
    publish.add_argument("--images", type=Path, required=True)
    args = parser.parse_args()
    try:
        project, root, product_root = project_paths(args.project)
        if args.command == "people":
            value = catalog(root)
        elif args.command == "products":
            value = products(product_root)
        else:
            root.mkdir(parents=True, exist_ok=True)
            with (root / ".save.lock").open("a") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                value = save(root, args)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(value, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
