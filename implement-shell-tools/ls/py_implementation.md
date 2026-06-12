# Python Implementation Notes — `ls`

This document explains the key decisions behind `ls.py`.

---

## Sorting: `key=str.casefold`

```python
entries = sorted(os.listdir(path), key=str.casefold)
```

`os.listdir` returns entries in filesystem order (arbitrary). `sorted()` with no key would sort by byte value — uppercase letters (`A`=65) sort before lowercase (`a`=97), so `README.md` would appear before `dir`. macOS `ls` sorts case-insensitively: `README.md` and `dir` are treated as if they were both lowercase for comparison purposes. `str.casefold` is the correct key for this — it is stronger than `str.lower` for non-ASCII characters.

---

## `os.listdir` never returns `.` and `..`

```python
if show_all:
    print('.')
    print('..')
    for entry in entries:
        print(entry)
```

`os.listdir` explicitly omits `.` (current directory) and `..` (parent directory) from its results, unlike C's `readdir` which does return them. When `-a` is active, `.` and `..` must be printed manually, always as the first two entries, before the sorted list.

---

## File path argument (known limitation)

Currently `os.listdir(path)` is called even when `path` is a regular file, which raises `NotADirectoryError` and exits 1. Real `ls` prints the file path and exits 0. This is tracked in `error.md`. The fix is to check `os.path.isfile(path)` before calling `listdir`.

---

## Unknown flags (known limitation)

Unknown flags (e.g. `-z`) are currently silently treated as the path argument. Real `ls` prints an error and exits 1. The fix is to detect arguments starting with `-` that are not `-1` or `-a` and print the "illegal option" error.

---

## `print` vs `sys.stdout.write`

`print(entry)` is used here instead of `sys.stdout.write`. Since we're only writing filenames (one per line, no line-ending edge cases), `print`'s automatic newline is fine. There's no risk of double-newlines — filenames never contain trailing newlines.

---

## Summary of edge cases handled

| Scenario | How it is handled |
|---|---|
| Directory not found | `OSError` caught → `e.strerror` printed to stderr → exit 1 |
| `-a` flag | `.` and `..` prepended manually before sorted entries |
| Case-insensitive sort | `key=str.casefold` |
| File path instead of dir | Not handled — exits 1 with wrong error (tracked in `error.md`) |
