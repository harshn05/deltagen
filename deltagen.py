"""
Copyright (c) 2026 Harsh Kumar Narula <harsh.narula@iitbombay.org>
"""

import os
import hashlib
import json
import zipfile
import sys
import argparse

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def normalize_path(path):
    return os.path.normpath(path)

def walk_with_depth(base_dir, max_depth=-1):
    """
    Custom folder traversal with depth control.
    max_depth = 0: Only files in base_dir
    max_depth = 1: Base dir + 1 level subdirectories
    max_depth = -1: Infinite recursion (all subdirectories)
    """
    base_dir = os.path.abspath(base_dir)
    file_map = {}

    for root, dirs, files in os.walk(base_dir):
        # Calculate current depth relative to base_dir
        rel_root = os.path.relpath(root, base_dir)
        if rel_root == ".":
            current_depth = 0
        else:
            current_depth = len(rel_root.split(os.sep))

        # Check depth limit
        if max_depth >= 0 and current_depth > max_depth:
            # Prevent os.walk from entering deeper directories
            dirs.clear()
            continue

        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, base_dir).replace('\\', '/')
            file_map[rel_path] = full_path

    return file_map

def create_delta(dir_a, dir_b, json_output="manifest.json", create_zip_file=False, zip_output="delta.zip", max_depth=-1):
    dir_a = normalize_path(dir_a)
    dir_b = normalize_path(dir_b)

    # Walk directories with specified max_depth
    files_a = walk_with_depth(dir_a, max_depth)
    files_b = walk_with_depth(dir_b, max_depth)

    print(f"Total files scanned in A (depth={max_depth}): {len(files_a)}")
    print(f"Total files scanned in B (depth={max_depth}): {len(files_b)}")

    manifest = []

    # Check Added & Modified
    for rel_path, path_b in files_b.items():
        if rel_path not in files_a:
            print(f"[ADD] {rel_path}")
            manifest.append({"type": "ADD", "path": rel_path})
        else:
            hash_a = get_file_hash(files_a[rel_path])
            hash_b = get_file_hash(path_b)
            if hash_a != hash_b:
                print(f"[MODIFY] {rel_path}")
                manifest.append({"type": "MODIFY", "path": rel_path})

    # Check Deleted
    for rel_path in files_a:
        if rel_path not in files_b:
            print(f"[DELETE] {rel_path}")
            manifest.append({"type": "DELETE", "path": rel_path})

    # 1. Save JSON File
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest saved to: {json_output}")

    # 2. Optional ZIP Creation
    if create_zip_file:
        with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))
            for item in manifest:
                if item["type"] in ["ADD", "MODIFY"]:
                    rel_path = item["path"]
                    path_b = files_b[rel_path]
                    zf.write(path_b, arcname=os.path.join("content", rel_path))
        print(f"Delta ZIP generated: {zip_output}")

    print(f"Total changes found: {len(manifest)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate delta manifest between two directories with depth control.")
    parser.add_argument("dir_a", help="Path to Directory A")
    parser.add_argument("dir_b", help="Path to Directory B")
    parser.add_argument("--depth", type=int, default=-1, help="Depth of recursion (0 = top folder only, 1 = 1 level subfolder, -1 = infinite)")
    parser.add_argument("--json", default="manifest.json", help="JSON output file path (default: manifest.json)")
    parser.add_argument("--zip", action="store_true", help="Include this flag if you also want to generate a ZIP file")
    
    args = parser.parse_args()
    create_delta(
        args.dir_a, 
        args.dir_b, 
        json_output=args.json, 
        create_zip_file=args.zip, 
        max_depth=args.depth
    )