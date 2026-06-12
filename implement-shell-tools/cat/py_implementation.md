# Python Implementation Notes — `cat`

This document explains the key decisions behind `cat.py`.

---

## Core loop: `process_lines`

```python
def process_lines(f, flag_n, flag_b):
    line_num = 0
    for line in f:
        ...
        sys.stdout.write(line)
```

**Why iterate `for line in f`?**
Python file objects are iterators — each iteration yields one line including its trailing `\n`. This is the idiomatic way to read line-by-line without loading the whole file into memory.

**Why `sys.stdout.write` instead of `print`?**
`print(line)` adds a newline. Since `line` already ends with `\n` (from the file), you'd get a double newline after each line. `sys.stdout.write` writes the string exactly as-is.

**Why is `line_num` local to the function?**
Each call to `process_lines` starts with a fresh `line_num = 0`. This is what resets the counter per file — the Python version gets this automatically from how function scope works, unlike the C version which has to explicitly reset a shared pointer.

---

## Blank line detection for `-b`

```python
if line.rstrip('\n') == '':
```

`rstrip('\n')` removes the trailing newline, leaving the content. If that's empty, the line is blank. This handles both `\n` (Unix) and the edge case where a file ends without a newline on the last line.

---

## stdout flush ordering

Real `cat` interleaves file content and errors in the order arguments are processed. Python's `sys.stdout` is block-buffered — it holds output in a buffer until the buffer is full or the program exits. `sys.stderr` flushes immediately. Without an explicit flush, error messages from a missing file can appear before the buffered output from the previous good file.

**Fix:** Call `sys.stdout.flush()` after finishing each file (relevant when fixed — currently the implementation does not do this, tracked in `error.md`).

---

## Error handling

```python
except OSError as e:
    print(f"cat: {filepath}: {e.strerror}", file=sys.stderr)
    exit_code = 1
```

`e.strerror` gives the human-readable OS error string (e.g. "No such file or directory") without the file path or error code prefix that `str(e)` would include. Real `cat` uses `strerror(errno)` — this matches it exactly.

The loop `continue`s to the next file on error, and the exit code is set to 1 at the end. The program does not stop on a bad file.

---

## Summary of edge cases handled

| Scenario | How it is handled |
|---|---|
| File not found | `OSError` caught → `e.strerror` printed to stderr → continue |
| No arguments | Reads from `sys.stdin` |
| `-b` + `-n` together | Last flag wins (no explicit precedence — known limitation vs. real `cat`) |
| Line counter per file | Automatic — `line_num` is local to each `process_lines` call |
