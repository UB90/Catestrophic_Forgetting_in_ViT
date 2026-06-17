import os
import csv
import shutil
from pathlib import Path
from PIL import Image
from collections import defaultdict

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}

def iter_images(root: Path):
    for dirpath, _, filenames in os.walk(root):
        for fname in sorted(filenames):
            fpath = Path(dirpath) / fname
            if fpath.suffix.lower() in IMAGE_EXTENSIONS:
                yield fpath

def execute(actions):
    for act in actions:
        if act["action"] == "count":
            _do_count(act)
        elif act["action"] == "detail":
            _do_detail(act)
        elif act["action"] == "verify":
            _do_verify(act)
        elif act["action"] == "resize":
            _do_resize(act)
        elif act["action"] == "convert":
            _do_convert(act)
        elif act["action"] == "rename":
            _do_rename(act)
        else:
            print(f"Unknown action: {act['action']}")

def _do_count(act):
    dataset = Path(act["dataset"])
    print(f"\nCOUNT {dataset}")
    total = 0
    for domain in sorted(dataset.iterdir()):
        if not domain.is_dir():
            continue
        domain_total = 0
        class_counts = {}
        for class_dir in sorted(domain.iterdir()):
            if not class_dir.is_dir():
                continue
            n = sum(1 for _ in iter_images(class_dir))
            class_counts[class_dir.name] = n
            domain_total += n
        print(f"  Domain {domain.name}: {domain_total} images")
        for cls, n in class_counts.items():
            print(f"    {cls}: {n}")
        total += domain_total
    print(f"TOTAL: {total}\n")

def _do_detail(act):
    dataset = Path(act["dataset"])
    outfile = Path(act["output"])
    rows = []
    for img in iter_images(dataset):
        with Image.open(img) as im:
            w, h = im.size
            mode = im.mode
        rows.append({"file": str(img), "width": w, "height": h, "mode": mode})
    outfile.parent.mkdir(parents=True, exist_ok=True)
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "width", "height", "mode"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {outfile}")

def _do_verify(act):
    dataset = Path(act["dataset"])
    for img in iter_images(dataset):
        with Image.open(img) as im:
            im.verify()
    print("All images OK")

def _do_resize(act):
    dataset = Path(act["dataset"])
    outdir = Path(act["outdir"])
    for w, h in act["resolutions"]:
        dest_root = outdir / f"{w}x{h}"
        for img in iter_images(dataset):
            dest = dest_root / img.relative_to(dataset)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(img) as im:
                im.resize((w, h), Image.LANCZOS).save(dest)
        print(f"Resized to {w}x{h} → {dest_root}")

def _do_convert(act):
    dataset = Path(act["dataset"])
    outdir = Path(act["outdir"])
    mode = "RGB" if act["format"] == "rgb" else "L"
    for img in iter_images(dataset):
        dest = outdir / img.relative_to(dataset)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(img) as im:
            im.convert(mode).save(dest)
    print(f"Converted to {act['format']} → {outdir}")

def _do_rename(act):
    dataset = Path(act["dataset"])
    outdir = Path(act["outdir"])
    new_ext = act.get("format") 

   
    classes = defaultdict(list)
    for img in iter_images(dataset):
        classes[img.parent.name].append(img)

    for class_name, files in classes.items():
        files.sort(key=lambda p: p.name)
        for idx, img in enumerate(files, start=1):
            rel_path = img.relative_to(dataset)
            if new_ext:
                new_name = f"{class_name}_{idx}.{new_ext}"
            else:
                new_name = f"{class_name}_{idx}{img.suffix}"
            dest = outdir / rel_path.parent / new_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(img), str(dest))
    print(f"Renamed and moved all images → {outdir}")