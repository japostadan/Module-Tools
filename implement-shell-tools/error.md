# Error Scenarios — Gap Analysis

Compared each tool's error output against the real macOS tool using `diff`.

---

## cat

### 1. Mixed good/bad files — stderr/stdout ordering
**Real:**
```
Once upon a time...
cat: sample-files/nope.txt: No such file or directory
There was a house made of gingerbread.
```
**Ours:**
```
cat: sample-files/nope.txt: No such file or directory
Once upon a time...
There was a house made of gingerbread.
```
**Root cause:** `sys.stdout.write()` is block-buffered; `print(..., file=sys.stderr)` flushes immediately.
The error from `nope.txt` appears before `1.txt`'s output because stdout hasn't been flushed yet.
**Fix:** Call `sys.stdout.flush()` after finishing each file.

### 2. Invalid flag — not detected
**Real:**
```
cat: illegal option -- z
usage: cat [-belnstuv] [file ...]
```
**Ours:** Treats `-z` as a filename → tries to open it, prints a file-not-found error.
**Fix:** Detect unknown flags (args starting with `-`) and print the real error + usage, then exit 1.

---

## ls

### 1. File path instead of directory
**Real:** `ls -1 sample-files/1.txt` → prints `sample-files/1.txt` and exits 0.
**Ours:** Errors with `ls: sample-files/1.txt: Not a directory` and exits 1.
**Root cause:** We call `os.listdir()` on the path unconditionally; it raises IsADirectoryError on a file.
**Fix:** If path is a file (not a directory), just print the path and exit 0.

### 2. Invalid flag message format
**Real:** `ls: invalid option -- z`
**Ours:** `ls: invalid option -- '-z'` (extra quotes and the full flag including dash)
**Fix:** Strip the leading `-` and remove the quotes from the error message.

---

## wc

### 1. Directory error says "open" instead of "read" (Python)
**Real:** `wc: sample-files: read: Is a directory`
**Ours (Python):** `wc: sample-files: open: Is a directory`
**Root cause:** We catch `OSError` from `open()`, so we label it "open". Real `wc` labels it "read".
**Fix:** For `IsADirectoryError` specifically, use "read" as the operation label.

### 2. Directory silently returns zero counts (C)
**Real:** `wc: sample-files: read: Is a directory`
**Ours (C):** `       0       0       0 sample-files` (no error, exit 0)
**Root cause:** On macOS, `fopen()` on a directory succeeds — it opens the directory entry.
`fgetc()` immediately returns EOF so the counter stays at zero.
**Fix:** Use `stat()` to check `S_ISDIR` before calling `fopen`. Print the "read: Is a directory" error and skip the file.

### 3. Directory error message is raw Node error string (JS)
**Real:** `wc: sample-files: read: Is a directory`
**Ours (JS):** `wc: sample-files: open: EISDIR: illegal operation on a directory, read`
**Root cause:** The `osError()` helper doesn't map `EISDIR` — it falls through to `err.message` which contains the full Node error string.
**Fix:** Add `if (err.code === 'EISDIR') return 'read: Is a directory'` to the `osError` helper (note: the label must be `read:`, not `open:`).

### 4. Invalid flag — not detected (Python, JS)
**Real:**
```
wc: illegal option -- z
usage: wc [-Lclmw] [file ...]
```
**Ours:** Treats `-z` as a filename → tries to open it.
**Fix:** Detect unknown flags and print the real error + usage, then exit 1.

---

## cat

### 3. Line counter not reset between files — C only
**Real:** `cat -n file1.txt file2.txt` → each file starts numbering at 1.
**Ours (C):** Line counter continues from the previous file's last line number.
**Root cause:** `line_num` is declared once in `main` and passed by pointer into `process_stream`. The same value persists across all files.
**Fix:** Reset `line_num = 0` before each `process_stream` call in the file loop.

---

## ls

### 3. File path error message wrong (JS)
**Real:** `ls -1 sample-files/1.txt` → prints `sample-files/1.txt`, exits 0.
**Ours (JS):** Calls `readdirSync` on the file path → catches ENOTDIR → `osError` maps it to "No such file or directory" (wrong code) → exits 1.
**Root cause:** The `osError` helper only maps `EACCES` and `ENOENT`. `ENOTDIR` falls through to `err.message`.
**Fix:** Before calling `readdirSync`, check `fs.statSync(path).isFile()`. If true, print the path and exit 0.
