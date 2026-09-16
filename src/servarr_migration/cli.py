import argparse
import os
import sys
from pathlib import Path

from servarr_migration.copier import ensure_directory, should_copy, transfer
from servarr_migration.crawler import iter_transfers
from servarr_migration.progress import FileBar


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog='servarr-migration',
        description=(
            'Copy files from a source directory to a target directory, '
            'preserving the source folder structure and skipping files '
            'that already exist in the target.'
        ),
    )
    parser.add_argument('source', type=Path, help='source directory')
    parser.add_argument('target', type=Path, help='target directory')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='show what would be copied without copying',
    )
    parser.add_argument(
        '--size-check',
        action='store_true',
        help='also skip files whose target size matches the source',
    )
    return parser.parse_args(argv)


def run(source, target, size_check=False, dry_run=False, out=sys.stdout,
        err=sys.stderr, show_progress=None):
    """Transfer missing files and return (copied, skipped, failed)."""
    source = Path(source)
    target = Path(target)
    if show_progress is None:
        show_progress = err.isatty()
    copied = 0
    skipped = 0
    failed = 0
    for source_file, target_file in iter_transfers(source, target):
        relative = source_file.relative_to(source)
        if not should_copy(source_file, target_file, size_check):
            skipped += 1
            continue
        bar = None
        if not dry_run:
            bar = FileBar(relative, show=show_progress, file=err)
        try:
            transfer(source_file, target_file, size_check, dry_run,
                     on_progress=bar)
        except OSError as error:
            if bar is not None:
                bar.close()
            failed += 1
            print(f'error  {relative}: {error}', file=err)
            continue
        if bar is not None:
            bar.close()
        copied += 1
        action = 'would copy' if dry_run else 'copied'
        print(f'{action}  {relative}', file=out)
    return copied, skipped, failed


def main(argv=None):
    """Run the CLI and return a process exit code."""
    args = parse_args(argv)
    if not args.source.is_dir():
        print(f'error: source is not a directory: {args.source}',
              file=sys.stderr)
        return 1
    if not os.access(args.source, os.R_OK | os.X_OK):
        print(f'error: source is not readable: {args.source}',
              file=sys.stderr)
        return 1
    try:
        ensure_directory(args.target)
    except OSError as error:
        print(f'error: cannot create target directory: {args.target} '
              f'({error.strerror})', file=sys.stderr)
        return 1
    copied, skipped, failed = run(
        args.source,
        args.target,
        size_check=args.size_check,
        dry_run=args.dry_run,
    )
    verb = 'would copy' if args.dry_run else 'copied'
    print(f'{verb}: {copied}, skipped: {skipped}, failed: {failed}')
    return 1 if failed else 0
