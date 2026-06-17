# Catastrophic Forgetting in Vision Transformers (ViT)

> **🚧 Project Status:** Just started on June 13, 2026. Currently, only a mini-project — a custom image preprocessing DSL — has been committed as a supporting tool for the main research. More components will be added as the project progresses.

Research project investigating catastrophic forgetting in Vision Transformers using the **Office-31** domain adaptation benchmark dataset.

## Project Structure

```
Catestrophic_Forgetting_in_ViT/
├── dsl/                        # Image Preprocessing DSL
│   ├── parser.py               # LALR grammar (inline) + Lark transformer
│   ├── executor.py             # Action dispatcher & image processing functions
│   ├── main.py                 # CLI entry point
│   └── test_office31.imgprep   # Example DSL script for Office-31
├── Office-31/                  # Dataset (not tracked in git)
│   ├── amazon/                 # 2817 product images (31 classes)
│   ├── dslr/                   #  498 DSLR photos   (31 classes)
│   └── webcam/                 #  795 webcam images  (31 classes)
├── README.md
├── .gitignore
└── .venv/                      # Virtual environment (not tracked)
```

## Dataset

**Office-31** — a standard domain adaptation benchmark containing 4,110 images across 3 domains and 31 object categories (e.g., back_pack, bike, keyboard, monitor, etc.).

| Domain | Images | Source |
|--------|-------:|--------|
| Amazon | 2,817 | Product catalog images |
| DSLR | 498 | High-resolution DSLR photos |
| Webcam | 795 | Low-resolution webcam captures |

---

## Image Preprocessing DSL

A custom Domain-Specific Language (`.imgprep`) for declarative image preprocessing pipelines. Write human-readable scripts instead of boilerplate Python.

### Setup

**Prerequisites:**

- Python 3.9+
- Conda (recommended) or pip

**Using the `vit` conda environment (recommended):**

```bash
conda activate vit
```

**Dependencies:**

| Package | Version | Purpose |
|---------|---------|---------|
| `lark` | ≥ 1.3 | LALR parser for the DSL grammar |
| `Pillow` | ≥ 9.0 | Image I/O, resize, and conversion |

Install manually if needed:

```bash
pip install lark Pillow
```

### Usage

```bash
cd dsl
python main.py <script.imgprep>
```

**Example:**

```bash
python main.py test_office31.imgprep
```

### DSL Language Reference

#### Comments

```
# This is a comment (lines starting with # are ignored)
```

#### `count` — Count images per class

```
count "path/to/dataset"
```

Walks the dataset directory structure and prints the number of images per domain and class.

#### `detail` — Export image metadata to CSV

```
detail "path/to/dataset" to "path/to/output.csv"
```

Produces a CSV with columns: `file`, `width`, `height`, `mode` for every image.

#### `verify` — Check for corrupt images

```
verify "path/to/dataset"
```

Opens and verifies every image; reports any that fail Pillow's integrity check.

#### `resize` — Resize images to target resolutions

```
resize "path/to/dataset" to 128x128, 256x256 in "path/to/output"
```

Creates a subfolder per resolution (e.g., `output/128x128/`, `output/256x256/`) preserving the original directory hierarchy. Uses Lanczos resampling.

#### `convert` — Convert image color mode

```
convert "path/to/dataset" to rgb in "path/to/output"
```

Supported modes: `rgb`, `grayscale`, `l`, `rgba`.

#### `rename` — Rename and reorganize images

```
rename "path/to/dataset" to "path/to/output" as png
```

Renames images sequentially by class (e.g., `keyboard_1.png`, `keyboard_2.png`) and optionally converts to a target format (`png`, `jpg`, `jpeg`, `bmp`, `tiff`). The original directory hierarchy is preserved.

### Example Script (`test_office31.imgprep`)

```
# Office-31 preprocessing script

count "D:/Catestrophic_Forgetting_in_ViT/Office-31"

detail "D:/Catestrophic_Forgetting_in_ViT/Office-31" to "D:/Catestrophic_Forgetting_in_ViT/office31_metadata.csv"

verify "D:/Catestrophic_Forgetting_in_ViT/Office-31"

resize "D:/Catestrophic_Forgetting_in_ViT/Office-31" to 128x128, 256x256 in "D:/Catestrophic_Forgetting_in_ViT/resized_office31"

convert "D:/Catestrophic_Forgetting_in_ViT/Office-31" to rgb in "D:/Catestrophic_Forgetting_in_ViT/office31_rgb"

rename "D:/Catestrophic_Forgetting_in_ViT/Office-31" to "D:/Catestrophic_Forgetting_in_ViT/office31_renamed" as png
```

### Architecture

```
.imgprep file
    │
    ▼
┌──────────────────────┐
│  parser.py            │  Inline LALR grammar + ScriptTransformer
│  parse_script(text)   │  Parses DSL text → list of action dicts
└──────────┬───────────┘
           │  List[dict]
           ▼
┌──────────────────────────────┐
│  executor.py                  │  execute(actions) dispatches each action
│  _do_count / _do_detail /     │  to the appropriate handler function
│  _do_verify / _do_resize /    │
│  _do_convert / _do_rename     │
└──────────────────────────────┘
```

---
