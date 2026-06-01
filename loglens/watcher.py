import os
import time
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class _LogFileHandler(FileSystemEventHandler):
    def __init__(self, filepath: str, callback: Callable[[str], None]) -> None:
        self._filepath = os.path.normcase(os.path.abspath(filepath))
        self._callback = callback
        self._pos = Path(filepath).stat().st_size

    def on_modified(self, event) -> None:
        if event.is_directory:
            return
        if os.path.normcase(os.path.abspath(event.src_path)) != self._filepath:
            return
        self._drain()

    def _drain(self) -> None:
        try:
            with open(self._filepath, "r", encoding="utf-8", errors="replace") as fh:
                fh.seek(self._pos)
                for line in fh:
                    stripped = line.rstrip("\n")
                    if stripped.strip():
                        self._callback(stripped)
                self._pos = fh.tell()
        except OSError:
            pass


def watch_file(filepath: str, callback: Callable[[str], None], tail_lines: int = 10) -> None:
    """Stream new lines from *filepath* to *callback* until KeyboardInterrupt."""
    # Print the last tail_lines of existing content first
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            existing = [l.rstrip("\n") for l in fh if l.strip()]
        for line in existing[-tail_lines:]:
            callback(line)
    except OSError:
        pass

    handler = _LogFileHandler(filepath, callback)
    observer = Observer()
    observer.schedule(handler, str(Path(filepath).parent.resolve()), recursive=False)
    observer.start()
    try:
        while observer.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
