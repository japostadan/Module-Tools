# Python Implementation Notes — `wc`

This document explains the key decisions behind `wc.py`.

---

## Binary mode: `open(filepath, 'rb')`

```python
with open(filepath, 'rb') as f:
    content = f.read()
```

`wc -c` counts bytes, not characters. In text mode, Python decodes the file using the system encoding — `len(content)` would give character count, which differs from byte count for non-ASCII files (e.g. a 2-byte UTF-8 character counts as 1 character but 2 bytes). Binary mode returns raw bytes so `len(content)` is always the byte count.

This also means `content` is a `bytes` object, not a `str`.

---

## Counting on `bytes` objects

```python
def count_bytes(content):
    lines = content.count(b'\n')
    words = len(content.split())
    chars = len(content)
```

**Lines:** `bytes.count(b'\n')` counts newline bytes directly — no need to split into lines.

**Words:** `bytes.split()` splits on any whitespace byte (space, tab, newline, carriage return). Each resulting non-empty segment is a word. This matches `wc`'s definition of a word exactly.

**Chars (bytes):** `len(content)` on a `bytes` object is the byte count.

---

## Directory error: `IsADirectoryError` before `OSError`

```python
except IsADirectoryError:
    print(f"wc: {filepath}: read: Is a directory", file=sys.stderr)
    exit_code = 1
except OSError as e:
    print(f"wc: {filepath}: open: {e.strerror}", file=sys.stderr)
    exit_code = 1
```

`IsADirectoryError` is a subclass of `OSError`. Python's `except` clauses are checked in order — if `OSError` came first, it would catch everything including `IsADirectoryError`, and we'd never reach the second branch.

The error labels matter: real `wc` says `read:` for directories and `open:` for other errors. Catching them separately is how we apply the right label to each case.

---

## Output format: `f"{lines:8}{words:8}{chars:8}"`

```python
print(f"{lines:8}{words:8}{chars:8}{suffix}")
```

`{:8}` right-aligns integers in an 8-character field. Real `wc` uses no separator between the three numbers — the alignment creates visual separation. The filename follows after a space (`suffix = f" {label}"`).

---

## Total row condition

```python
if len(files) > 1:
    print_row(total_lines, total_words, total_chars, 'total', ...)
```

The total is printed only when more than one file was given. Note: the condition checks the number of input files, not the number of successfully counted files. If two files are given and one errors, the total row still appears (with the counts from the successful file only).

---

## Summary of edge cases handled

| Scenario | How it is handled |
|---|---|
| File not found | `OSError` caught → `e.strerror` → `open:` label → continue |
| Directory argument | `IsADirectoryError` caught → `read:` label → continue |
| No files given | `sys.stdin.buffer.read()` (binary) for accurate byte count |
| Multiple files | Accumulates totals; prints `total` row |
| Byte vs character count | Binary mode ensures `len()` = bytes |
