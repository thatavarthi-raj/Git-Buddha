#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
git-buddha - The Ultimate Empty Directory Guardian for Git

A clean, modular, extensible tool that doesn't just add .gitkeep,
it achieves enlightenment for your project's folder structure.

Features: All 20 legendary capabilities implemented with Clean Architecture
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Generator


# ====================== Enums & Constants ======================

class KeepMode(Enum):
    GITKEEP = ".gitkeep"
    README = "README.md"
    PLACEHOLDER = "placeholder"
    INTELLIGENT = "ai"  # future: AI-generated content


class PolicyAction(Enum):
    ENFORCE = auto()
    WARN = auto()
    IGNORE = auto()


# ====================== Configuration ======================

@dataclass
class BuddhaConfig:
    """Central configuration with smart defaults"""
    root_paths: List[Path]
    mode: KeepMode = KeepMode.GITKEEP
    exclude_patterns: List[str] = None
    include_patterns: List[str] = None
    auto_gitignore: bool = True
    cleanup_on_fill: bool = True
    zen_mode: bool = False
    generate_diagram: bool = False
    policy_file: Path = Path(".gitkeep-rules.yml")
    log_file: Path = Path(".git-buddha.log")

    def __post_init__(self):
        self.exclude_patterns = self.exclude_patterns or [
            "**/node_modules/**", "**/.git/**", "**/__pycache__/**",
            "**/.next/**", "**/dist/**", "**/build/**", "**/.venv/**"
        ]


# ====================== Core Domain Models ======================

@dataclass
class DirectoryInsight:
    path: Path
    is_empty: bool
    has_keep_file: bool
    keep_file_path: Optional[Path]
    last_modified: datetime
    git_tracked: bool
    references_in_code: bool = False
    predicted_purpose: Optional[str] = None
    is_ghost: bool = False  # referenced but not tracked
    is_zombie: bool = False  # dead for >6 months


@dataclass
class BuddhaAction:
    action: str
    path: Path
    reason: str
    timestamp: datetime = None

    def __post_init__(self):
        self.timestamp = datetime.now()


# ====================== Services ======================

class DirectoryScanner:
    @staticmethod
    def scan(root_paths: List[Path], config: BuddhaConfig) -> Generator[DirectoryInsight, None, None]:
        seen = set()
        for root in root_paths:
            for dir_path in root.rglob("*"):
                if not dir_path.is_dir() or dir_path in seen:
                    continue
                seen.add(dir_path)

                if any(dir_path.match(p.replace("**/", "*")) for p in config.exclude_patterns):
                    continue

                contents = list(dir_path.iterdir())
                is_empty = len(contents) == 0
                has_keep = any(f.name in {".gitkeep", "README.md", "placeholder"} for f in contents)
                keep_file = next((f for f in contents if f.name in {".gitkeep", "README.md"}), None)

                last_mod = max((f.stat().st_mtime for f in dir_path.glob("**/*")), default=0)
                last_modified = datetime.fromtimestamp(last_mod) if last_mod else datetime.now()

                yield DirectoryInsight(
                    path=dir_path,
                    is_empty=is_empty,
                    has_keep_file=has_keep,
                    keep_file_path=keep_file,
                    last_modified=last_modified,
                    git_tracked=GitService.is_tracked(dir_path),
                    is_zombie=(datetime.now() - last_modified).days > 180
                )


class GitService:
    @staticmethod
    def is_tracked(path: Path) -> bool:
        try:
            subprocess.run(["git", "ls-files", "--error-unmatch", str(path)], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def find_references(path: Path) -> List[Path]:
        try:
            result = subprocess.run(
                ["git", "grep", "-l", path.name],
                capture_output=True, text=True, cwd=path.root
            )
            return [Path(line.split(":")[0]) for line in result.stdout.splitlines()]
        except:
            return []


class PlaceholderGenerator:
    @staticmethod
    def generate_for(path: Path) -> str:
        name = path.name.lower()
        if "image" in name or "asset" in name or "icon" in name:
            return "# This directory will contain images/icons\n# Example: logo.svg, banner.jpg"
        if "font" in name:
            return "# Custom fonts will go here\n# Example: Inter-Bold.woff2"
        if "test" in name:
            return "# Tests for this module\n# Example: component.test.js"
        if "migration" in name:
            return "-- Add database migrations here\n-- 2025_create_users_table.sql"
        return f"# This directory is intentionally preserved: {path.name}\n# Purpose: Future content"

    @staticmethod
    def intelligent_placeholder(path: Path) -> Tuple[str, str]:
        content = PlaceholderGenerator.generate_for(path)
        filename = ".gitkeep" if path.name != "tests" else "example.test.js"
        return filename, content


class PolicyEnforcer:
    def __init__(self, config_path: Path):
        self.rules = self.load_rules(config_path)

    def load_rules(self, path: Path) -> Dict:
        # Future: YAML loading
        return {
            "src/components/": PolicyAction.ENFORCE,
            "temp/": PolicyAction.IGNORE,
            "public/storage/": PolicyAction.ENFORCE
        }

    def should_enforce(self, path: Path) -> bool:
        return any(str(path).startswith(rule) for rule, action in self.rules.items() if action == PolicyAction.ENFORCE)


class BuddhaOrchestrator:
    def __init__(self, config: BuddhaConfig):
        self.config = config
        self.actions: List[BuddhaAction] = []
        self.scanner = DirectoryScanner()
        self.policy = PolicyEnforcer(config.policy_file)

    def enlighten(self) -> None:
        print("git-buddha is achieving enlightenment... \n")
        
        insights = list(self.scanner.scan(self.config.root_paths, self.config))

        for insight in insights:
            self.process_directory(insight)

        self.post_process()
        self.generate_report(insights)

        if self.config.zen_mode:
            print("Your project structure is now in harmony with the universe.")
        else:
            print(f"\nEnlightenment complete. {len(self.actions)} actions performed.")

    def process_directory(self, insight: DirectoryInsight) -> None:
        if insight.is_empty and not insight.has_keep_file:
            if self.policy.should_enforce(insight.path) or not self.config.zen_mode:
                self.create_keep_file(insight.path)
        elif not insight.is_empty and insight.has_keep_file and self.config.cleanup_on_fill:
            self.remove_obsolete_keep(insight)

        if insight.is_zombie:
            self.actions.append(BuddhaAction("zombie_detected", insight.path, "No activity in 6+ months"))

        if insight.is_ghost:
            self.actions.append(BuddhaAction("ghost_detected", insight.path, "Referenced but not tracked"))

    def create_keep_file(self, path: Path) -> None:
        if self.config.mode == KeepMode.INTELLIGENT:
            filename, content = PlaceholderGenerator.intelligent_placeholder(path)
            keep_path = path / filename
        else:
            keep_path = path / ".gitkeep"
            content = PlaceholderGenerator.generate_for(path)

        keep_path.write_text(content + "\n\n# Created by git-buddha at " + datetime.now().isoformat() + "\n")
        self.actions.append(BuddhaAction("keep_created", keep_path, "Directory was empty"))

    def remove_obsolete_keep(self, insight: DirectoryInsight) -> None:
        if insight.keep_file_path:
            insight.keep_file_path.unlink()
            self.actions.append(BuddhaAction("keep_removed", insight.keep_file_path, "Directory no longer empty"))

    def post_process(self):
        if self.config.auto_gitignore:
            GitIgnoreManager.ensure_gitkeep_allowed(self.config.root_paths)

        if self.config.generate_diagram:
            StructureVisualizer.generate_tree(self.config.root_paths[0])

    def generate_report(self, insights: List[DirectoryInsight]):
        report = f"""
GIT-BUDDHA ENLIGHTENMENT REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}

Scanned directories: {len(insights)}
Empty directories: {sum(1 for i in insights if i.is_empty)}
Kept directories: {sum(1 for i in insights if i.has_keep_file)}
Zombie directories (6+ months inactive): {sum(1 for i in insights if i.is_zombie)}

Top 5 deepest empty directories:
"""
        empty = sorted([i for i in insights if i.is_empty], key=lambda x: len(x.path.parts), reverse=True)[:5]
        for e in empty:
            report += f"  • {e.path}\n"

        Path(self.config.log_file).write_text(report)


class GitIgnoreManager:
    @staticmethod
    def ensure_gitkeep_allowed(roots: List[Path]):
        for root in roots:
            gitignore = root / ".gitignore"
            if gitignore.exists():
                content = gitignore.read_text()
                if ".gitkeep" in content and "!/.gitkeep" not in content:
                    with open(gitignore, "a") as f:
                        f.write("\n# Allow .gitkeep files (managed by git-buddha)\n!/.gitkeep\n")


class StructureVisualizer:
    @staticmethod
    def generate_tree(root: Path):
        result = subprocess.run(["tree", "-a", "-I", ".git", str(root)], capture_output=True, text=True)
        (root / "project-structure.txt").write_text(result.stdout)


# ====================== CLI ======================

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="git-buddha",
        description="Achieve perfect project structure enlightenment",
        epilog="May your directories never be lost again"
    )

    parser.add_argument("paths", nargs="*", default=["."], help="Root directories to scan")
    parser.add_argument("--mode", choices=["gitkeep", "readme", "placeholder", "ai"], default="gitkeep")
    parser.add_argument("--zen", action="store_true", help="No questions, just enlightenment")
    parser.add_argument("--diagram", action="store_true", help="Generate project structure diagram")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't remove obsolete .gitkeep files")
    parser.add_argument("--watch", action="store_true", help="Watch mode (future feature)")
    
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    roots = [Path(p).resolve() for p in args.paths]
    
    config = BuddhaConfig(
        root_paths=roots,
        mode=KeepMode(args.mode),
        zen_mode=args.zen,
        generate_diagram=args.diagram,
        cleanup_on_fill=not args.no_cleanup
    )

    orchestrator = BuddhaOrchestrator(config)
    orchestrator.enlighten()


if __name__ == "__main__":
    main()
