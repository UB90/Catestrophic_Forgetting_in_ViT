"""
Executor for the .imgprep preprocessing DSL.

Provides two classes consumed by main.py:
  - PreprocessingTransformer : Lark Transformer  →  list[action-dict]
  - PreprocessingExecutor    : runs each action-dict against the filesystem
"""

import csv
import os
import shutil
from pathlib import Path

from lark import Transformer, Token
from PIL import Image


# ═══════════════════════════════════════════════════════════════════════
#  Transformer – AST  →  list of action dicts
# ═══════════════════════════════════════════════════════════════════════

class PreprocessingTransformer(Transformer):
    """Converts a Lark parse-tree into a flat list of action dictionaries."""

    # ── helpers ──────────────────────────────────────────────────────
    @staticmethod
    def _unquote(token: Token) -> str:
        """Strip surrounding double-quotes from an ESCAPED_STRING token."""
        return str(token).strip('"')

    # ── rules ────────────────────────────────────────────────────────
    def start(self, items):
        # Filter out None / empty items produced by blank lines
        return [i for i in items if i is not None]

    def count_stmt(self, items):
        return {"action": "count", "dataset": self._unquote(items[0])}

    def detail_stmt(self, items):
        return {
            "action": "detail",
            "dataset": self._unquote(items[0]),
            "output": self._unquote(items[1]),
        }

    def verify_stmt(self, items):
        return {"action": "verify", "dataset": self._unquote(items[0])}

    def resize_stmt(self, items):
        return {
            "action": "resize",
            "dataset": self._unquote(items[0]),
            "resolutions": items[1],          # list from resolution_list
            "outdir": self._unquote(items[2]),
        }

    def convert_stmt(self, items):
        return {
            "action": "convert",
            "dataset": self._unquote(items[0]),
            "format": str(items[1]),
            "outdir": self._unquote(items[2]),
        }

    def resolution_list(self, items):
        """Return a list of (w, h) tuples."""
        resolutions = []
        for tok in items:
            w, h = str(tok).split("x")
            resolutions.append((int(w), int(h)))
        return resolutions


# ═══════════════════════════════════════════════════════════════════════
#  Executor – runs each action dict
# ═══════════════════════════════════════════════════════════════════════

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}


def _iter_images(root: Path):
    """Recursively yield all image paths under *root*."""
    for dirpath, _, filenames in os.walk(root):
        for fname in sorted(filenames):
            fpath = Path(dirpath) / fname
            if fpath.suffix.lower() in IMAGE_EXTENSIONS:
                yield fpath


class PreprocessingExecutor:
    """Executes a list of action-dicts produced by PreprocessingTransformer."""

    def __init__(self, actions: list[dict]):
        self.actions = actions

    # ── dispatcher ───────────────────────────────────────────────────
    def run(self):
        for action in self.actions:
            handler = getattr(self, f"_do_{action['action']}", None)
            if handler is None:
                print(f"[WARN] Unknown action: {action['action']}")
                continue
            handler(action)

    # ── COUNT ────────────────────────────────────────────────────────
    def _do_count(self, action: dict):
        dataset = Path(action["dataset"])
        print(f"\n{'='*60}")
        print(f"  COUNT  –  {dataset}")
        print(f"{'='*60}")

        if not dataset.exists():
            print(f"  [ERROR] Dataset path does not exist: {dataset}")
            return

        # Walk top-level subdirectories (domains) then class folders
        total = 0
        for domain in sorted(dataset.iterdir()):
            if not domain.is_dir():
                continue
            domain_total = 0
            class_counts = {}
            for cls_dir in sorted(domain.iterdir()):
                if not cls_dir.is_dir():
                    continue
                n = sum(1 for _ in _iter_images(cls_dir))
                class_counts[cls_dir.name] = n
                domain_total += n

            print(f"\n  Domain: {domain.name}  ({domain_total} images)")
            for cls_name, n in class_counts.items():
                print(f"    {cls_name:.<30s} {n}")
            total += domain_total

        print(f"\n  TOTAL images: {total}\n")

    # ── DETAIL ───────────────────────────────────────────────────────
    def _do_detail(self, action: dict):
        dataset = Path(action["dataset"])
        output = Path(action["output"])
        print(f"\n{'='*60}")
        print(f"  DETAIL  –  {dataset}  →  {output}")
        print(f"{'='*60}")

        if not dataset.exists():
            print(f"  [ERROR] Dataset path does not exist: {dataset}")
            return

        output.parent.mkdir(parents=True, exist_ok=True)
        rows = []
        for img_path in _iter_images(dataset):
            try:
                with Image.open(img_path) as im:
                    w, h = im.size
                    mode = im.mode
                rows.append({
                    "file": str(img_path),
                    "width": w,
                    "height": h,
                    "mode": mode,
                })
            except Exception as exc:
                rows.append({
                    "file": str(img_path),
                    "width": "ERR",
                    "height": "ERR",
                    "mode": str(exc),
                })

        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["file", "width", "height", "mode"])
            writer.writeheader()
            writer.writerows(rows)

        print(f"  Wrote {len(rows)} rows to {output}\n")

    # ── VERIFY ───────────────────────────────────────────────────────
    def _do_verify(self, action: dict):
        dataset = Path(action["dataset"])
        print(f"\n{'='*60}")
        print(f"  VERIFY (corrupt)  –  {dataset}")
        print(f"{'='*60}")

        if not dataset.exists():
            print(f"  [ERROR] Dataset path does not exist: {dataset}")
            return

        corrupt = []
        checked = 0
        for img_path in _iter_images(dataset):
            checked += 1
            try:
                with Image.open(img_path) as im:
                    im.verify()
            except Exception as exc:
                corrupt.append((img_path, str(exc)))

        if corrupt:
            print(f"\n  Found {len(corrupt)} corrupt image(s):")
            for p, err in corrupt:
                print(f"    ✗ {p}  –  {err}")
        else:
            print(f"\n  All {checked} images are valid ✓")
        print()

    # ── RESIZE ───────────────────────────────────────────────────────
    def _do_resize(self, action: dict):
        dataset = Path(action["dataset"])
        resolutions = action["resolutions"]       # list[(w,h)]
        outdir = Path(action["outdir"])
        print(f"\n{'='*60}")
        print(f"  RESIZE  –  {dataset}")
        print(f"  Resolutions: {', '.join(f'{w}x{h}' for w, h in resolutions)}")
        print(f"  Output:      {outdir}")
        print(f"{'='*60}")

        if not dataset.exists():
            print(f"  [ERROR] Dataset path does not exist: {dataset}")
            return

        for w, h in resolutions:
            res_dir = outdir / f"{w}x{h}"
            count = 0
            for img_path in _iter_images(dataset):
                rel = img_path.relative_to(dataset)
                dest = res_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                try:
                    with Image.open(img_path) as im:
                        resized = im.resize((w, h), Image.LANCZOS)
                        resized.save(dest)
                    count += 1
                except Exception as exc:
                    print(f"    [SKIP] {img_path}: {exc}")

            print(f"  {w}x{h}: resized {count} images → {res_dir}")
        print()

    # ── CONVERT ──────────────────────────────────────────────────────
    def _do_convert(self, action: dict):
        dataset = Path(action["dataset"])
        fmt = action["format"]           # "rgb" or "grayscale"
        outdir = Path(action["outdir"])
        print(f"\n{'='*60}")
        print(f"  CONVERT  –  {dataset}  →  {fmt}")
        print(f"  Output:     {outdir}")
        print(f"{'='*60}")

        if not dataset.exists():
            print(f"  [ERROR] Dataset path does not exist: {dataset}")
            return

        pil_mode = "RGB" if fmt == "rgb" else "L"
        count = 0
        for img_path in _iter_images(dataset):
            rel = img_path.relative_to(dataset)
            dest = outdir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                with Image.open(img_path) as im:
                    converted = im.convert(pil_mode)
                    converted.save(dest)
                count += 1
            except Exception as exc:
                print(f"    [SKIP] {img_path}: {exc}")

        print(f"  Converted {count} images to {fmt} → {outdir}\n")
