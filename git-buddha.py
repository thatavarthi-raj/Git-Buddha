#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
git-buddha - The Ultimate Empty Directory Guardian
Achieve perfect project structure enlightenment
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List
import argparse
import sys

@dataclass
class Config:
    roots: List[Path]
    zen: bool = False

def preserve_empty_dirs(roots: List[Path], zen: bool = False):
    preserved = 0
    for root in roots:
        for dirpath in root.rglob("*"):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                keep = dirpath / ".gitkeep"
                content = f"# This directory is intentionally preserved by git-buddha\n# Purpose: {dirpath.name}\n# Created: {datetime.now():%Y-%m-%d %H:%M}\n"
                keep.write_text(content, encoding="utf-8")
                preserved += 1
                if not zen:
                    print(f"Preserved: {dirpath}")
    if zen:
        print("Your project structure is now in harmony with the universe.")
    elif preserved == 0:
        print("No empty directories found. Already enlightened.")
    else:
        print(f"Enlightenment complete. {preserved} directories preserved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="git-buddha",
        description="Achieve perfect Git project structure enlightenment"
    )
    parser.add_argument("paths", nargs="*", default=["."], help="Directories to scan")
    parser.add_argument("--zen", action="store_true", help="Pure enlightenment mode")
    args = parser.parse_args()
    
    roots = [Path(p).resolve() for p in args.paths]
    preserve_empty_dirs(roots, args.zen)
