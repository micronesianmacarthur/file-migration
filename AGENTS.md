# AGENTS.md

Guidance for humans and AI agents working in this repository.

## Project

`servarr-migration` is a CLI tool that copies files from a source directory to a
target directory, preserving the source folder structure, and only copying files
that are missing from the target.

## Stack & tooling

- Language: Python >= 3.14 (see `.python-version` and `pyproject.toml`)
- Dependency/project management: `uv`
- Runtime: `uv run python ...`
- Dependencies: prefer the standard library; `tqdm` is used for progress bars
- Lint/format: none installed yet; follow PEP 8 manually (see below)
- Tests: none configured yet; add when the codebase grows

## Commands

- Run the CLI: `uv run python main.py <source_dir> <target_dir>`
- Add a dependency: `uv add <package>`
- Add a dev dependency: `uv add --dev <package>`
- Run tests (when added): `uv run pytest`

## Conventions

### PEP 8

- 4-space indentation, no tabs; max line length 79 characters.
- Blank lines: two between top-level functions/classes, one inside methods.
- Imports: one per line, grouped in this order with a blank line between groups:
  1. standard library
  2. third-party
  3. local
- Naming: `snake_case` for functions/variables, `PascalCase` for classes,
  `UPPER_SNAKE_CASE` for constants, `_leading_underscore` for private members.
- Use single quotes for strings unless the string contains a single quote.
- Surround binary operators with spaces; no spaces around keyword-only `=` in
  function signatures.
- Avoid `from x import *` and overly long chained expressions.

### Separation of concerns

Keep responsibilities in distinct modules/units inside a `src/servarr_migration`
package instead of piling everything into `main.py`:

- `cli.py` — argument parsing, user-facing I/O, and running the program. No
  filesystem/copy logic.
- `crawler.py` (or `scanner.py`) — discovering source files and mapping them to
  relative target paths.
- `copier.py` — deciding whether a file is missing and performing the copy.
  No argument parsing, no printing.
- `progress.py` — progress-bar rendering via `tqdm`. No filesystem/copy logic.
- `main.py` — thin entry point that wires the pieces together.

General rules:

- Each function does one thing and is testable in isolation.
- Modules only talk to each other through small, explicit functions.
- I/O (parsing/printing) stays out of logic modules; filesystem logic stays out
  of the CLI.
- Prefer small helper functions over deeply nested control flow.
- Return values over side effects where a choice must be made elsewhere.

## CLI contract

- Positional arg 1: source directory; positional arg 2: target directory.
- Exit code 0 on success, non-zero on error.
- A per-file progress bar is shown when stderr is a TTY; pass
  `show_progress=True/False` to `cli.run()` to override.