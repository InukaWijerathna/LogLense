from loglense.watcher import watch_file


def test_watch_file_replays_tail_lines_then_streams_new_ones(tmp_path):
    log_path = tmp_path / "app.log"
    log_path.write_text("line1\nline2\nline3\n", encoding="utf-8")

    seen = []
    stop_after = {"count": 0}

    class _StoppableObserver:
        """Fake watchdog Observer that lets us end the loop deterministically."""

        def __init__(self):
            self.alive = True

        def schedule(self, *_a, **_kw):
            pass

        def start(self):
            # Simulate a new line being appended, then stop the loop.
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write("line4\n")

        def is_alive(self):
            stop_after["count"] += 1
            return stop_after["count"] < 2

        def stop(self):
            self.alive = False

        def join(self):
            pass

    import loglense.watcher as watcher_module

    original_observer = watcher_module.Observer
    watcher_module.Observer = _StoppableObserver
    try:
        watch_file(str(log_path), seen.append, tail_lines=2)
    finally:
        watcher_module.Observer = original_observer

    # Only the last 2 existing lines are replayed on start.
    assert seen == ["line2", "line3"]


def test_watch_file_missing_file_warns_but_does_not_raise(tmp_path, capsys):
    missing = tmp_path / "missing.log"

    class _NoOpObserver:
        def schedule(self, *_a, **_kw):
            pass

        def start(self):
            pass

        def is_alive(self):
            return False

        def stop(self):
            pass

        def join(self):
            pass

    import loglense.watcher as watcher_module

    original_observer = watcher_module.Observer
    watcher_module.Observer = _NoOpObserver
    try:
        watch_file(str(missing), lambda _line: None, tail_lines=5)
    finally:
        watcher_module.Observer = original_observer

    err = capsys.readouterr().err
    assert "warning" in err.lower()
