# Concepts: Implement Shell Tools

These are the underlying ideas that make `cat`, `ls`, and `wc` work the way they do.
Understanding these concepts will help you reason about any Unix CLI tool, not just these three.

---

## 1. Standard Streams (stdin, stdout, stderr)

Every Unix process starts with three open "files" called **standard streams**:

| Stream | FD | Variable | Default destination |
|--------|-----|----------|-------------------|
| stdin  | 0   | `sys.stdin`  | keyboard |
| stdout | 1   | `sys.stdout` | terminal |
| stderr | 2   | `sys.stderr` | terminal |

**FD** = file descriptor, a small integer the OS assigns to every open file.

```
keyboard ──▶ [ stdin (0) ] ──▶ your program ──▶ [ stdout (1) ] ──▶ terminal
                                                 [ stderr (2) ] ──▶ terminal
```

### Why two output streams?

stdout is for **normal output** (the data). stderr is for **error messages**.
This lets you redirect one without the other:

```bash
python3 wc.py *.txt > counts.txt        # stdout → file, errors still print to terminal
python3 cat.py *.txt 2>/dev/null        # suppress errors, output still prints
python3 cat.py *.txt > out.txt 2>&1     # both to the same file
```

### In Python

```python
sys.stdout.write("normal output\n")
print("error message", file=sys.stderr)   # same as sys.stderr.write(...)

# stdin as a file — reads from keyboard (or piped input)
for line in sys.stdin:
    ...
```

---

## 2. Buffering

**Buffering** = the OS/runtime holds data in memory and writes it to the destination in chunks rather than immediately. This is faster, but can cause output to appear out of order.

### The three buffering modes

| Mode | When data is flushed | Used for |
|------|---------------------|---------|
| **Unbuffered** | Every write, immediately | `sys.stderr` |
| **Line-buffered** | At each `\n` | stdout when connected to a terminal |
| **Block-buffered** | When the buffer fills (~8 KB) or explicitly flushed | stdout when piped or redirected |

### The bug this caused in cat

```
cat 1.txt MISSING.txt 2.txt
Once upon a time...          ← stdout (buffered, held in memory)
cat: MISSING.txt: No such…   ← stderr (flushed immediately) ← appears FIRST
There was a house…           ← stdout (buffered, still in memory)
```

The error prints before the first file's output because stderr is already on screen while stdout is still in the buffer.

**Fix:** call `sys.stdout.flush()` after each file to force the buffer to empty:
```python
with open(filepath) as f:
    print_lines(f, ...)
sys.stdout.flush()   # ← drain the buffer before moving to the next file
```

### Manual flushing
```python
sys.stdout.flush()          # flush stdout explicitly
print("hi", flush=True)     # print() has a built-in flush parameter
```

---

## 3. Exit Codes

When a process finishes, it reports a number to the shell — the **exit code**.

| Code | Meaning |
|------|---------|
| `0`  | success |
| `1`  | general error |
| `2`  | misuse of the command (bad flag, wrong usage) |

```bash
cat missing.txt
echo $?   # → 1

cat existing.txt
echo $?   # → 0
```

### In Python

```python
sys.exit(0)   # success
sys.exit(1)   # failure
# no call = implicit sys.exit(0)
```

### Why it matters

Scripts use exit codes to make decisions:
```bash
if python3 wc.py file.txt > /dev/null 2>&1; then
    echo "file is readable"
else
    echo "something went wrong"
fi
```

### Partial failure

`cat` and `wc` continue processing remaining files even if one fails, and exit 1 at the end. They don't stop at the first error:
```
cat 1.txt MISSING.txt 2.txt   → prints 1.txt, prints error, prints 2.txt, exits 1
```

---

## 4. sys.argv — How Arguments Reach Your Program

When you run `python3 wc.py -l sample-files/3.txt`, the shell splits this into a list and passes it to the program:

```python
sys.argv == ['wc.py', '-l', 'sample-files/3.txt']
#            [0]       [1]   [2]
# sys.argv[0] = the script name
# sys.argv[1:] = everything after = what you actually want
```

### Shell globbing happens before your program sees it

`python3 wc.py sample-files/*` — the shell expands `*` into a list of matching filenames **before** calling your program. Your program never sees the `*`:

```python
sys.argv == ['wc.py', 'sample-files/1.txt', 'sample-files/2.txt', 'sample-files/3.txt']
```

This is why `wc sample-files/*` lists each file separately — the shell did the expansion.

### Parsing flags

Real tools parse flags character-by-character to support combined flags:

```python
# This means: -l AND -w at the same time
args = ['-lw', 'file.txt']

for arg in args:
    if arg.startswith('-'):
        for ch in arg[1:]:     # iterates 'l', then 'w'
            if ch == 'l': flag_l = True
            elif ch == 'w': flag_w = True
```

---

## 5. Binary Mode vs Text Mode

When you open a file, Python (and the OS) can treat it two ways:

| Mode | `open()` call | What Python does |
|------|--------------|-----------------|
| **Text mode** | `open(f)` or `open(f, 'r')` | Decodes bytes → str using UTF-8; translates `\r\n` → `\n` on Windows |
| **Binary mode** | `open(f, 'rb')` | Returns raw bytes, no translation |

### Why wc uses binary mode

`wc -c` counts **bytes**, not characters. For ASCII files they're the same, but for files with multi-byte characters (e.g. `é` is 2 bytes in UTF-8):

```python
s = "café"
len(s)            # → 4 characters
len(s.encode())   # → 5 bytes (é = 2 bytes)
```

```python
# WRONG: counts characters
with open('file.txt') as f:
    print(len(f.read()))   # could be less than wc -c

# CORRECT: counts bytes
with open('file.txt', 'rb') as f:
    print(len(f.read()))   # matches wc -c exactly
```

### stdin in binary mode

For `wc` reading from stdin, use `sys.stdin.buffer` (the raw binary version of stdin):
```python
content = sys.stdin.buffer.read()   # bytes
content = sys.stdin.read()          # str (text mode, may differ in byte count)
```

---

## 6. Newlines and Line Counting

A **newline** is just a byte with value `0x0A`, written as `\n`.

### How wc counts lines

`wc -l` counts the number of `\n` bytes — not the number of "visual lines":

```
file contents: "hello\nworld\n"   → wc says 2 lines  ✓
file contents: "hello\nworld"     → wc says 1 line   (no trailing \n)
file contents: ""                 → wc says 0 lines
```

```python
lines = content.count(b'\n')   # binary: count the newline byte
```

### Why sys.stdout.write() instead of print()

`print(line)` always adds a `\n` at the end. If `line` already ends with `\n`, you get a blank line between every line:

```python
line = "hello\n"
print(line)             # outputs: "hello\n\n"  ← double newline
sys.stdout.write(line)  # outputs: "hello\n"    ← correct
```

---

## 7. File Permissions and OSError

Unix assigns **read/write/execute** permissions to every file for three groups: owner, group, others.

```
-rw-r--r-- 1 user group 125 file.txt
 ↑↑↑ ↑↑↑ ↑↑↑
 owner  group  others
 rw-    r--    r--
```

When you try to open a file you don't have permission to read, the OS refuses and Python raises an `OSError`:

```python
try:
    with open('/etc/shadow', 'rb') as f:   # no permission
        ...
except OSError as e:
    print(e.strerror)   # "Permission denied"
    print(e.errno)      # 13  (POSIX error code)
```

### The OSError hierarchy

```
OSError
├── FileNotFoundError    (errno 2:  ENOENT — file doesn't exist)
├── PermissionError      (errno 13: EACCES — no permission)
├── IsADirectoryError    (errno 21: EISDIR — it's a directory, not a file)
└── NotADirectoryError   (errno 20: ENOTDIR — expected a directory, got a file)
```

All of these are subclasses of `OSError`. If you catch `OSError` first, it catches all of them — so put specific subclasses before the generic one:

```python
# CORRECT order — specific first
except IsADirectoryError as e:
    print(f"wc: {path}: read: {e.strerror}")   # "Is a directory"
except OSError as e:
    print(f"wc: {path}: open: {e.strerror}")   # everything else

# WRONG order — IsADirectoryError is never reached
except OSError as e:        # catches IsADirectoryError too
    ...
except IsADirectoryError:   # dead code
    ...
```

---

## 8. os.listdir() and the Filesystem

`os.listdir(path)` asks the OS for the **directory entries** at that path — the filenames stored in that directory.

### What it returns (and what it doesn't)

```python
os.listdir('sample-files')
# → ['1.txt', '2.txt', '3.txt', '.hidden.txt', 'dir']
# Never includes '.' or '..'
# Includes hidden files (those starting with '.')
```

`.` (current dir) and `..` (parent dir) are implicit in every directory but `listdir` omits them. Real `ls -a` shows them — you add them manually:

```python
if show_all:
    print('.')
    print('..')
    for entry in entries:
        print(entry)
```

### Sorting and locale

Default Python sort: byte-order → uppercase letters (A=65) come before lowercase (a=97):
```python
sorted(['readme.md', 'Makefile'])   # → ['Makefile', 'readme.md']
```

macOS `ls` sorts case-insensitively:
```python
sorted(['readme.md', 'Makefile'], key=str.casefold)   # → ['Makefile', 'readme.md'] ✓
# casefold() lowercases everything for comparison only — display name is unchanged
```

---

## 9. The Unix Philosophy

These three tools embody the Unix design principle:

> **Each program does one thing well. Programs work together through text streams.**

### How composability works

Tools read from stdin and write to stdout, so they chain with `|` (pipes):

```bash
# the shell connects stdout of ls to stdin of wc
ls -1 sample-files | wc -l   # → count files in a directory
```

Under the hood, the shell creates a **pipe** — a kernel buffer — and sets `ls`'s stdout (fd 1) to the write end and `wc`'s stdin (fd 0) to the read end. Both programs just read/write their standard streams; they don't know about each other.

### Why reading stdin is the same as reading a file

In our implementations, `print_lines(sys.stdin, ...)` works the same as `print_lines(file_obj, ...)` because both are **file-like objects** that support `for line in f`. The program doesn't need to know whether it's reading a file or a pipe.

```python
# Same function handles both a real file and stdin
if not files:
    print_lines(sys.stdin, flag_n, flag_b)      # reads from keyboard or pipe
else:
    with open(filepath) as f:
        print_lines(f, flag_n, flag_b)          # reads from a file
```

---

## Quick Reference

| Concept | Where you saw it | Key line |
|---------|-----------------|----------|
| stdout flush | cat, ordering bug | `sys.stdout.flush()` after each file |
| binary mode | wc byte count | `open(f, 'rb')` |
| stdin binary | wc stdin | `sys.stdin.buffer.read()` |
| case-insensitive sort | ls | `sorted(entries, key=str.casefold)` |
| OSError subclass order | wc directory error | `IsADirectoryError` before `OSError` |
| exit codes | all tools | `sys.exit(0)` / `sys.exit(1)` |
| combined flag parsing | all tools | `for ch in arg[1:]` |
| no double newline | cat | `sys.stdout.write(line)` not `print(line)` |
| line count = `\n` count | wc | `content.count(b'\n')` |
