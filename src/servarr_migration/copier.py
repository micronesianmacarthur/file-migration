import shutil
from pathlib import Path

from servarr_migration.progress import CHUNK_SIZE


def ensure_directory(path):
    """Create path and any missing parents."""
    Path(path).mkdir(parents=True, exist_ok=True)


def should_copy(source, target, size_check=False):
    """Return True when the target is missing or differs in size."""
    target = Path(target)
    if not target.exists():
        return True
    if not size_check:
        return False
    return target.stat().st_size != Path(source).stat().st_size


def copy_file(source, target, on_progress=None):
    """Copy source to target in chunks, reporting byte progress."""
    source = Path(source)
    target = Path(target)
    total = source.stat().st_size
    target.parent.mkdir(parents=True, exist_ok=True)
    copied = 0
    if on_progress is not None:
        on_progress(0, total)
    with source.open('rb') as src, target.open('wb') as dst:
        while chunk := src.read(CHUNK_SIZE):
            dst.write(chunk)
            copied += len(chunk)
            if on_progress is not None:
                on_progress(copied, total)
    shutil.copystat(source, target)


def transfer(source, target, size_check=False, dry_run=False,
             on_progress=None):
    """Copy source to target when needed; return True if copied."""
    if not should_copy(source, target, size_check):
        return False
    if not dry_run:
        copy_file(source, target, on_progress=on_progress)
    return True
