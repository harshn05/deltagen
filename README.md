# DeltaGen 🚀

**DeltaGen** is a lightweight, cross-platform Python CLI utility designed to compute directory differences (deltas) between two folder structures ($A$ and $B$). It generates a structured `manifest.json` file detailing all added, modified, and deleted files, with optional support for depth-restricted recursion and delta ZIP packaging.

---

## ✨ Features

- **Recursive Directory Scan**: Traverses subdirectories recursively with configurable depth limits.
- **SHA-256 Checksum Matching**: Detects file modifications accurately using file hash comparison rather than just modification timestamps.
- **Cross-Platform Compatibility**: Normalizes file paths across Windows (`\`) and Unix/Linux/macOS (`/`).
- **Flexible Depth Control**: Control how deep the script should scan (`0` for top-level only, `1` for immediate subdirectories, `-1` for full depth).
- **JSON Manifest Generation**: Produces a clean, readable JSON format outlining `ADD`, `MODIFY`, and `DELETE` actions.
- **Optional Delta Bundling**: Easily generate a compressed `.zip` archive containing both the manifest and the new/modified file payloads.

---

## 📁 Manifest Output Format

The output `manifest.json` tracks every file change between Directory $A$ and Directory $B$:

```json
[
  {
    "type": "ADD",
    "path": "docs/new_guide.md"
  },
  {
    "type": "MODIFY",
    "path": "config/settings.json"
  },
  {
    "type": "DELETE",
    "path": "deprecated/old_script.py"
  }
]
```

---

## 🛠️ Requirements

- **Python 3.8+**
- No external libraries required (Uses standard library modules: `os`, `hashlib`, `json`, `zipfile`, `argparse`).

---

## 🚀 Usage

### Command Structure

```bash
python deltagen.py <dir_a> <dir_b> [options]
```

### Options & Arguments

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `dir_a` | Position | *Required* | Path to base directory $A$ |
| `dir_b` | Position | *Required* | Path to target/updated directory $B$ |
| `--depth` | Integer | `-1` | Recursion depth limit (`0` = top-level only, `1` = 1 sub-level, `-1` = full) |
| `--json` | String | `manifest.json` | Custom filename/path for the output JSON manifest |
| `--zip` | Flag | `False` | Includes changed content and manifest into a compressed `delta.zip` file |

---

## 💡 Examples

### 1. Basic Full Delta (JSON Manifest Only)
Compare `folder_a` and `folder_b` recursively and generate `manifest.json`:
```bash
python deltagen.py path/to/folder_a path/to/folder_b
```

### 2. Limit Recursion Depth
Only scan top-level files (ignore all sub-directories):
```bash
python deltagen.py path/to/folder_a path/to/folder_b --depth 0
```

Scan top-level files and 1 level of sub-directories:
```bash
python deltagen.py path/to/folder_a path/to/folder_b --depth 1
```

### 3. Generate a Delta ZIP Bundle
Create both the `manifest.json` and a `delta.zip` containing the modified/added files:
```bash
python deltagen.py path/to/folder_a path/to/folder_b --zip
```

### 4. Custom Output Path
Specify a custom JSON manifest name:
```bash
python deltagen.py path/to/folder_a path/to/folder_b --json output_diff.json
```

---

## 🔄 Recreating Directory B from Directory A

If you generate a delta ZIP using the `--zip` flag, you can reconstruct Directory $B$ using the following Python snippet:

```python
import os
import shutil
import json
import zipfile

def apply_delta(dir_a, delta_zip, target_b):
    # Copy base directory A to target location
    if os.path.exists(target_b):
        shutil.rmtree(target_b)
    shutil.copytree(dir_a, target_b)

    # Extract and apply manifest changes
    with zipfile.ZipFile(delta_zip, 'r') as zf:
        manifest = json.loads(zf.read("manifest.json").decode('utf-8'))
        
        for entry in manifest:
            action = entry["type"]
            rel_path = entry["path"]
            target_path = os.path.join(target_b, rel_path)

            if action in ["ADD", "MODIFY"]:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with zf.open(os.path.join("content", rel_path)) as src, open(target_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            elif action == "DELETE":
                if os.path.exists(target_path):
                    os.remove(target_path)

    print(f"Successfully reconstructed B at {target_path}")
```
