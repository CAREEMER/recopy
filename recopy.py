#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from fnmatch import fnmatch
import argparse

__version__ = "1.0.0"

CONFIG_FILE = "recopy.ignore"


def is_text_file(filepath):
    try:
        result = subprocess.run(
            ["file", "--mime-type", "-b", filepath],
            capture_output=True,
            text=True,
            timeout=5,
        )
        mime_type = result.stdout.strip()
        return mime_type.startswith("text/")
    except Exception:
        return False


def is_empty_content(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            return not content.strip()
    except Exception:
        return True


def read_config(config_path):
    patterns = []
    if not os.path.exists(config_path):
        return patterns

    config_dir = os.path.dirname(config_path) or "."

    with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            pattern = line.strip().rstrip("\r")
            if pattern and not pattern.startswith("#"):
                if pattern.startswith("./"):
                    pattern = os.path.join(config_dir, pattern[2:])
                elif not pattern.startswith("/"):
                    pattern = os.path.join(config_dir, pattern)
                patterns.append(pattern)

    return patterns


def should_exclude(filepath, exclude_patterns):
    for pattern in exclude_patterns:
        if "*" in pattern or "?" in pattern:
            if fnmatch(filepath, pattern):
                return True
        elif filepath == pattern or filepath.startswith(pattern + "/"):
            return True
    return False


def copy_to_clipboard(text):
    try:
        # macOS
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
        # Linux
        elif sys.platform.startswith("linux"):
            try:
                subprocess.run(["xclip", "-selection", "clipboard"],
                               input=text.encode("utf-8"), check=True)
            except FileNotFoundError:
                subprocess.run(["xsel", "--clipboard", "--input"],
                               input=text.encode("utf-8"), check=True)
        # Windows
        elif sys.platform == "win32":
            subprocess.run(["clip"], input=text.encode("utf-16"), check=True)
        else:
            return False
        return True
    except Exception as e:
        print(f"Warning: Could not copy to clipboard: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Recursively collect file contents with gitignore-like exclusion patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
          recopy                    # Collect all files and copy to clipboard
          recopy --no-clipboard     # Print to stdout instead
          recopy --stats            # Show statistics about processed files
        
        Configuration:
          Create 'recopy.ignore' files with exclusion patterns (glob supported):
            *.log
            ./temp/*
            node_modules/
            # This is a comment
        """
    )
    parser.add_argument(
        "--version", action="version", version=f"recopy {__version__}"
    )
    parser.add_argument(
        "--no-clipboard",
        action="store_true",
        help="Print output to stdout instead of copying to clipboard",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics about processed files",
    )
    parser.add_argument(
        "--config",
        default=CONFIG_FILE,
        help=f"Custom config file name (default: {CONFIG_FILE})",
    )

    args = parser.parse_args()
    config_file = args.config

    if not os.path.exists(config_file):
        Path(config_file).touch()
        print(f"Created {config_file}")

    exclude_patterns = []

    exclude_patterns.extend(read_config(config_file))

    for root, dirs, files in os.walk("."):
        if config_file in files:
            config_path = os.path.join(root, config_file)
            if config_path not in [f"./{config_file}", config_file]:
                exclude_patterns.extend(read_config(config_path))

    output = []
    stats = {"total": 0, "skipped": 0, "copied": 0, "errors": 0}

    for root, dirs, files in os.walk("."):
        for filename in files:
            stats["total"] += 1

            if filename == config_file:
                stats["skipped"] += 1
                continue

            filepath = os.path.join(root, filename)
            relative_path = filepath[2:] if filepath.startswith("./") else filepath

            if should_exclude(filepath, exclude_patterns):
                stats["skipped"] += 1
                continue

            if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
                stats["skipped"] += 1
                continue

            if not is_text_file(filepath):
                stats["skipped"] += 1
                continue

            if is_empty_content(filepath):
                stats["skipped"] += 1
                continue

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    output.append(f"filepath: {relative_path}")
                    output.append(content)
                    output.append("\n")
                    stats["copied"] += 1
            except Exception as e:
                print(f"Error reading {filepath}: {e}", file=sys.stderr)
                stats["errors"] += 1

    result = "\n".join(output)

    if args.no_clipboard:
        print(result)
    else:
        if copy_to_clipboard(result):
            print(f"✓ Copied {stats['copied']} files to clipboard")
        else:
            print(result)

    if args.stats:
        print(f"\nStatistics:", file=sys.stderr)
        print(f"  Total files scanned: {stats['total']}", file=sys.stderr)
        print(f"  Files copied: {stats['copied']}", file=sys.stderr)
        print(f"  Files skipped: {stats['skipped']}", file=sys.stderr)
        print(f"  Errors: {stats['errors']}", file=sys.stderr)


if __name__ == "__main__":
    main()
