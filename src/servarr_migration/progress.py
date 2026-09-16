import sys

from tqdm import tqdm


CHUNK_SIZE = 1024 * 1024


class FileBar:
    """Single-file byte progress bar backed by tqdm.

    Instances are callables: copier invokes them with the cumulative
    number of bytes copied and the file's total size.
    """

    def __init__(self, relative, show=True, file=sys.stderr):
        self._bar = tqdm(
            total=0,
            desc=str(relative),
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            leave=False,
            disable=not show,
            file=file,
        )

    def __call__(self, copied, total):
        self._bar.total = total
        delta = copied - self._bar.n
        if delta:
            self._bar.update(delta)
        if total == 0 or copied >= total:
            self._bar.refresh()

    def close(self):
        self._bar.close()
