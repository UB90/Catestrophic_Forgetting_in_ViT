# Catastrophic Forgetting in Vision Transformers (ViT)

> **🚧 Project Status:** Just started on June 13, 2026. Currently, only a mini-project — a custom image preprocessing DSL — has been committed as a supporting tool for the main research. More components (training, evaluation, analysis) will be added as the project progresses.

Research project investigating catastrophic forgetting in Vision Transformers using the **Office-31** domain adaptation benchmark dataset.

## Project Structure

```
Catestrophic_Forgetting_in_ViT/
├── dsl/                        # Image Preprocessing DSL
│   ├── preprocessing.lark      # LALR grammar definition
│   ├── parser.py               # Lark-based parser
│   ├── executor.py             # Transformer + Executor (runs DSL actions)
│   ├── main.py                 # CLI entry point
│   └── test_office31.imgprep   # Example DSL script for Office-31
├── Office-31/                  # Dataset (not tracked in git)
│   ├── amazon/                 # 2817 product images (31 classes)
│   ├── dslr/                   #  498 DSLR photos   (31 classes)
│   └── webcam/                 #  795 webcam images  (31 classes)
├── README.md
└── .gitignore
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
// This is a comment (ignored by the parser)
```

#### `count` — Count images per class

```
count dataset "path/to/dataset"
```

Walks the dataset directory structure and prints the number of images per domain and class.

#### `detail` — Export image metadata to CSV

```
detail dataset "path/to/dataset" output "path/to/output.csv"
```

Produces a CSV with columns: `file`, `width`, `height`, `mode` for every image.

#### `verify` — Check for corrupt images

```
verify dataset "path/to/dataset" corrupt
```

Opens and verifies every image; reports any that fail Pillow's integrity check.

#### `resize` — Resize images to target resolutions

```
resize dataset "path/to/dataset" to 32x32, 96x96 outdir "path/to/output"
```

Creates a subfolder per resolution (e.g., `output/32x32/`, `output/96x96/`) preserving the original directory hierarchy. Uses Lanczos resampling.

#### `convert` — Convert image color mode

```
convert dataset "path/to/dataset" to rgb outdir "path/to/output"
```

Supported formats: `rgb`, `grayscale`.

### Example Script (`test_office31.imgprep`)

```
// Count images per class (amazon, dslr, webcam)
count dataset "D:/Catestrophic_Forgetting_in_ViT/Office-31"

// Export resolution details
detail dataset "D:/Catestrophic_Forgetting_in_ViT/Office-31" output "D:/Catestrophic_Forgetting_in_ViT/office31_details.csv"

// Check for corrupt images
verify dataset "D:/Catestrophic_Forgetting_in_ViT/Office-31" corrupt

// Resize to 32x32 and 96x96 (preserves subfolder structure)
resize dataset "D:/Catestrophic_Forgetting_in_ViT/Office-31" to 32x32, 96x96 outdir "D:/Catestrophic_Forgetting_in_ViT/office31_resized"

// Convert all images to RGB (saves in separate folder)
convert dataset "D:/Catestrophic_Forgetting_in_ViT/Office-31" to rgb outdir "D:/Catestrophic_Forgetting_in_ViT/office31_rgb"
```

### Architecture

```
.imgprep file
    │
    ▼
┌──────────────────────┐
│  PreprocessingParser  │  parser.py — reads .lark grammar, produces parse tree
└──────────┬───────────┘
           │  Lark Tree
           ▼
┌──────────────────────────────┐
│  PreprocessingTransformer     │  executor.py — converts tree → action dicts
└──────────┬───────────────────┘
           │  List[dict]
           ▼
┌──────────────────────────────┐
│  PreprocessingExecutor        │  executor.py — dispatches & runs each action
└──────────────────────────────┘
```

---

## License

This project is for research and educational purposes.
