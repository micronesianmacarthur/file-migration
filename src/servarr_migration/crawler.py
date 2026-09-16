from pathlib import Path


def iter_relative_files(source):
    """Yield file paths relative to the source directory."""
    source = Path(source)
    for path in sorted(source.rglob('*')):
        if path.is_file():
            yield path.relative_to(source)


def iter_transfers(source, target):
    """Yield (source_file, target_file) pairs mirroring the tree."""
    source = Path(source)
    target = Path(target)
    for relative in iter_relative_files(source):
        yield source / relative, target / relative
