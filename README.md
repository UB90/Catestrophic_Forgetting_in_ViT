# ImagePrep_DSL


## Project Structure

```
ImagePrep_DSL/
└──dsl
|    ├── main.py              # CLI entry point; parses .imgprep scripts and executes actions
|    ├── parser.py            # LALR grammar (inline) + Lark transformer; defines DSL syntax
|    ├── executor.py          # Action dispatcher & image processing functions; implements all DSL commands
|    ├── test_office31.imgprep  # Example DSL script demonstrating all features on Office-31 dataset
└── README.md            # This file
```

**File Descriptions:**

- **main.py**: Entry point for the CLI. Reads a `.imgprep` script file and orchestrates parsing and execution.
- **parser.py**: Defines the DSL grammar in LALR format and implements a Lark transformer to convert parsed tokens into action dictionaries.
- **executor.py**: Contains the action dispatcher and all image processing implementations (count, detail, verify, resize, convert, rename).
- **test_office31.imgprep**: Example preprocessing script for the Office-31 dataset, demonstrating all DSL commands in sequence.

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

Walks the dataset directory structure and prints the number of images per domain and class, organized hierarchically:
- **Domain level**: Total count per domain (e.g., amazon, dslr, webcam)
- **Class level**: Individual image count per class within each domain
- **Overall total**: Grand total across all images

**Example output:**
```
COUNT path/to/dataset
  Domain amazon: 2817 images
    back_pack: 91
    bike: 87
    ...
  Domain dslr: 498 images
    back_pack: 10
    ...
TOTAL: 4110
```

#### `detail` — Export image metadata to CSV

```
detail "path/to/dataset" to "path/to/output.csv"
```

Exports metadata for all images in the dataset to a CSV file. Each row contains:
- **file**: Full path to the image
- **width**: Image width in pixels
- **height**: Image height in pixels
- **mode**: Image color mode (e.g., RGB, RGBA, L for grayscale)

**Example:**
```csv
file,width,height,mode
path/to/amazon/back_pack/image1.jpg,1024,768,RGB
path/to/amazon/back_pack/image2.jpg,800,600,RGB
```

#### `verify` — Validate image integrity

```
verify "path/to/dataset"
```

Validates all images in the dataset using PIL's built-in verification. Detects corrupted or malformed image files. Prints "All images OK" if all images pass validation.

#### `resize` — Resize images to multiple resolutions

```
resize "path/to/dataset" to RESolution1, RESolution2, ... in "path/to/output"
```

Resizes all images to specified dimensions. Supports multiple resolutions in a single command. Each resolution creates a subdirectory in the output folder (e.g., `128x128/`, `256x256/`). Uses high-quality Lanczos resampling.

**Example:**
```
resize "dataset" to 128x128, 256x256, 512x512 in "resized_output"
```

Creates:
```
resized_output/
├── 128x128/     (all images resized to 128×128)
├── 256x256/     (all images resized to 256×256)
└── 512x512/     (all images resized to 512×512)
```

#### `convert` — Convert image color mode

```
convert "path/to/dataset" to MODE in "path/to/output"
```

Converts all images to a specified color mode. Supported modes:
- `rgb` or `rgba`: Convert to RGB or RGBA (color)
- `grayscale` or `l`: Convert to grayscale (single-channel)

Preserves the original directory structure in the output folder.

**Example:**
```
convert "dataset" to grayscale in "grayscale_output"
```

#### `rename` — Rename and reorganize images

```
rename "path/to/dataset" to "path/to/output" as FORMAT
```

Renames all images to a consistent format: `ClassName_Index.extension`. Images are renamed per-class in sorted order and output to the specified directory. The directory structure is preserved.

**Example:**
```
rename "dataset" to "renamed_output" as png
```

Input structure:
```
dataset/
└── back_pack/
    ├── image_a.jpg
    ├── image_b.jpg
    └── image_c.jpg
```

Output structure:
```
renamed_output/
└── back_pack/
    ├── back_pack_1.png
    ├── back_pack_2.png
    └── back_pack_3.png
```

#### Supported Image Formats

The DSL supports the following image file extensions:
`.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.tiff`, `.webp`

---

## Example Script

Here is a complete example preprocessing pipeline for the Office-31 dataset:

```
# Count images in the dataset
count "Office-31"

# Export metadata to CSV
detail "Office-31" to "office31_metadata.csv"

# Verify all images are valid
verify "Office-31"

# Resize to common training sizes
resize "Office-31" to 128x128, 256x256 in "resized_office31"

# Convert all images to RGB
convert "Office-31" to rgb in "office31_rgb"

# Rename images with consistent naming and moves the data from original dataset to renamed_folder
rename "Office-31" to "office31_renamed" as png
```

Save this as `preprocess.imgprep` and run:

```bash
python main.py preprocess.imgprep
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

count "path/to/datset/Office-31"

detail "path/to/datset/Office-31" to "path/to/output/office31_metadata.csv"

verify "path/to/datset/Office-31"

resize "path/to/datset/Office-31" to 128x128, 256x256 in "path/to/output/resized_office31"

convert "path/to/datset/Office-31" to rgb in "Dpath/to/output/office31_rgb"

rename "path/to/datset/Office-31" to "path/to/output/office31_renamed" as png
```

### Architecture

```
.imgprep file
    │
    ▼
┌──────────────────────┐
│  parser.py           │  Inline LALR grammar + ScriptTransformer      
│  parse_script(text)  │  Parses DSL text → list of action dicts           
└──────────┬───────────┘
           │  List[dict]
           ▼
┌──────────────────────────────┐
│  executor.py                 │  execute(actions) dispatches each action         
│  _do_count / _do_detail /    │  to the appropriate     handler function               
│  _do_verify / _do_resize /   │
│  _do_convert / _do_rename    │
└──────────────────────────────┘
```

---
