<!-- Copied/created by AI assistant: focused, actionable instructions for code agents -->
# Git-Buddha — Copilot / AI Agent Instructions

Purpose: give an AI coding agent immediate, focused context so it can make safe, correct changes in this repository.

- **Primary entrypoint:** `git-buddha.py` — single-file Python CLI implementing scanning, placeholder generation, policy enforcement, and simple git integrations.
- **Quick run (local):** `python git-buddha.py .` — accepts multiple roots, see `--mode`, `--zen`, and `--diagram` flags.

Key concepts & design choices
- Filesystem-first: the tool uses `Path.rglob()` to discover directories; most logic is driven by directory contents and simple heuristics.
- Keep modes: `KeepMode` controls what is created (`.gitkeep`, `README.md`, `placeholder`, `ai`). See the `KeepMode` enum in `git-buddha.py`.
- Policy layer: a `PolicyEnforcer` reads `policy_file` (`.gitkeep-rules.yml`) and currently uses simple path-prefix rules mapped to `PolicyAction`.
- Git integration: `GitService` calls `git` commands (`ls-files`, `grep`) to determine tracking and references — code calls external git executable and sets `cwd` in some places.
- Output artifacts: `.git-buddha.log` (report), `project-structure.txt` (when `--diagram`), and written `.gitkeep`/`README.md` files in empty folders.

Developer workflows & debugging
- Run locally: `python git-buddha.py . --mode ai --diagram` to generate placeholders and the tree report.
- Zen/CI mode: `python git-buddha.py . --zen` is non-interactive and suitable for pre-commit or CI. Example pre-commit snippet: `git-buddha --zen`.
- Diagram generation uses the external `tree` command (invoked by `StructureVisualizer.generate_tree`). On Windows this may be missing — prefer running `--diagram` on environments with `tree`, or install `tree`/use WSL.
- Logs and reports: check `.git-buddha.log` at repo root after runs; `project-structure.txt` will appear in the scanned root when `--diagram` is used.

Project-specific patterns & conventions
- Default excludes: `node_modules`, `.git`, `__pycache__`, `.next`, `dist`, `build`, `.venv` — these are set in `BuddhaConfig.__post_init__`.
- Placeholder generation rules: `PlaceholderGenerator.generate_for()` contains deterministic string rules for names containing `image`, `icon`, `font`, `test`, `migration`. Use this when editing placeholder behavior.
- Intelligent mode: `PlaceholderGenerator.intelligent_placeholder()` returns `(filename, content)` — note tests get `example.test.js` as the filename in the current code.
- Gitignore handling: `GitIgnoreManager.ensure_gitkeep_allowed()` appends `!/.gitkeep` only when `.gitkeep` appears and the exception is missing.

Integration notes and gotchas (what to watch for)
- `GitService.find_references()` sets `cwd=path.root` — `Path.root` is the filesystem root (drive) and not necessarily the repository root; be careful when modifying reference search logic.
- Policy loader is a stub: `PolicyEnforcer.load_rules()` returns an in-memory dict (no YAML parsing yet). If you add real rules, update this loader to parse YAML.
- `StructureVisualizer` uses `subprocess.run(['tree' ...])` and writes stdout to `project-structure.txt`. If `tree` isn't present, the call may fail silently; add fallback logic when adding cross-platform features.

When changing behavior
- Keep changes minimal and localized: this is a single-file tool; prefer small, well-tested edits inside `git-buddha.py` rather than broad refactors.
- Respect existing defaults: avoid changing `BuddhaConfig` defaults unless adding a clear opt-in flag.
- If adding new CLI flags, update `create_parser()` and propagate into `BuddhaConfig` creation in `main()`.

Files to inspect for context (quick picks)
- `git-buddha.py` — main implementation (scan, placeholder, policy, gitignore, CLI)
- `README.md` — usage and example outputs
- `.gitkeep-rules.yml` — expected policy file (not present; create when needed)

If you need clarification
- Ask: which runtime env should the tool prioritize (native Windows vs. Unix/WSL)?
- Ask: should placeholders be localized or extended with metadata (author/timestamp) beyond the current footer?

Thanks — please run the script locally after edits and check `.git-buddha.log` and `project-structure.txt` for validation.
