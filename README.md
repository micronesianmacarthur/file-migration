# file-migration

A small CLI tool that copies files from a **source** directory to a **target**
directory, preserving the source folder structure, and only copies files that
are **missing** from the target. Existing files are never overwritten, so the
command is safe to run repeatedly (idempotent).

Built for migrating media libraries (e.g. Servarr-managed folders) between
disks without duplicating files that are already present.

## Features

- Mirrors the source tree into the target directory.
- Copies only missing files by default; optional size check detects partial or
  truncated copies.
- Per-file byte progress bar (via `tqdm`) when stderr is a terminal.
- Chunked copying that preserves file timestamps and permissions.
- Creates the target directory if it does not exist.
- `--dry-run` to preview without writing anything.
- Clear per-file error reporting and a non-zero exit code on failure.

## Requirements

- Python >= 3.14
- [`uv`](https://docs.astral.sh/uv/) for dependency management and running

## Install

Clone and sync dependencies:

```sh
git clone https://github.com/micronesianmacarthur/file-migration.git
cd file-migration
uv sync
```

## Usage

Pass the source directory first and the target directory second:

```sh
uv run python main.py <source_dir> <target_dir>
```

Example:

```sh
uv run python main.py /mnt/hdd/.servarr/data/media/ /media/gis/Essentials/servarr/media/
```

If the target directory does not exist, it is created (including parents).

### Options

| Option         | Description                                                        |
| -------------- | ------------------------------------------------------------------ |
| `--dry-run`    | Show what would be copied without copying anything.                |
| `--size-check` | Also re-copy files whose target size differs from the source.      |
| `-h`, `--help` | Show the help message and exit.                                    |

### Examples

Preview a migration:

```sh
uv run python main.py /source /target --dry-run
```

Re-copy files that were only partially copied (size mismatch):

```sh
uv run python main.py /source /target --size-check
```

### Progress bar

A per-file progress bar is shown automatically when stderr is a terminal. When
output is piped or redirected it is hidden. Call `cli.run(..., show_progress=True)`
to force it on or `show_progress=False` to force it off.

## How it works

1. Walk the source directory and compute each file's path relative to it.
2. Build the mirrored destination path under the target directory.
3. If the destination is missing (or differs in size with `--size-check`),
   create its parent directories and copy it in 1 MiB chunks, preserving
   metadata.
4. Report copied, skipped, and failed counts.

A file that already exists in the target is left untouched.

## Project layout

```
main.py                          Thin entry point
src/servarr_migration/
  cli.py                         Argument parsing, I/O, orchestration
  crawler.py                     Discover source files, map to target paths
  copier.py                      Decide missing files and perform copies
  progress.py                    Per-file progress bar (tqdm)
```

## Development

Run the tool:

```sh
uv run python main.py <source_dir> <target_dir>
```

See `AGENTS.md` for coding conventions and architecture guidelines.

## Exit codes

- `0` — success (including a run that copied nothing).
- `1` — invalid source, unreadable source, target that cannot be created, or
  one or more files failed to copy.
