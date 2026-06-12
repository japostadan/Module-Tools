# C Implementation Notes — `wc`

This document explains the key decisions behind `wc.c`.

---

## Compile flags

```bash
gcc -Wall -Wextra -Werror -o wc wc.c
```

---

## `Counts` struct

```c
typedef struct { long lines, words, chars; } Counts;
```

Grouping the three counters into a struct lets `count_stream` return all three values at once. Without it you'd need to pass three pointers as output parameters, or use global variables. The struct is returned by value — C copies it on return, which is fine for a 24-byte struct.

**Why `long` and not `int`?**
A file can have more lines or bytes than fit in a 32-bit int (max ~2 billion). `long` is at least 32 bits on all platforms and 64 bits on most modern 64-bit systems, covering any realistic file size.

---

## `count_stream` — character-by-character reading

```c
static Counts count_stream(FILE *f) {
    Counts c = {0, 0, 0};
    int ch, in_word = 0;
    while ((ch = fgetc(f)) != EOF) {
        c.chars++;
        if (ch == '\n') c.lines++;
        if (ch == ' ' || ch == '\t' || ch == '\n' || ch == '\r') {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            c.words++;
        }
    }
    return c;
}
```

**Why `fgetc` (character-by-character) instead of reading lines?**
`wc` counts bytes directly — there is no need to buffer whole lines. `fgetc` is the simplest way to count every byte without any allocation.

**Why `int ch` and not `char ch`?**
`fgetc` returns `int`, not `char`. The return value `EOF` is typically `-1`, which would be lost if assigned to `char` (signed char overflow) or misinterpreted as a valid byte (unsigned char). Using `int` preserves the full range of possible return values.

**Word counting with `in_word` flag:**
A word starts when a non-whitespace character is seen after whitespace (or the beginning of the file). `in_word` tracks whether we are currently inside a word, so each word is counted exactly once — on the transition from whitespace to non-whitespace.

---

## Directory detection with `stat`

```c
struct stat st;
if (stat(files[i], &st) == 0 && S_ISDIR(st.st_mode)) {
    fprintf(stderr, "wc: %s: read: Is a directory\n", files[i]);
    exit_code = 1;
    continue;
}
```

On macOS, `fopen` on a directory succeeds — it opens the directory as a file descriptor. `fgetc` then immediately returns `EOF`, producing zero counts with no error. To match real `wc`'s behavior (`read: Is a directory`), a `stat` check is done before `fopen`. `S_ISDIR(st.st_mode)` checks the directory bit in the mode flags.

The error label is `read:` not `open:` — this matches the exact format of macOS `wc`.

---

## Binary mode: `"rb"`

```c
FILE *f = fopen(files[i], "rb");
```

`"rb"` (read binary) prevents the C runtime from translating line endings. On macOS this makes no practical difference (Unix uses `\n` only), but `"rb"` guarantees that `c.chars` counts raw bytes, not characters — matching `wc -c` semantics. Text mode (`"r"`) could silently alter byte counts on other platforms.

---

## `print_row` — 8-char columns

```c
printf("%8ld%8ld%8ld %s\n", c.lines, c.words, c.chars, label);
```

Real `wc` right-aligns each number in an 8-character field with no separator between numbers. The space before the filename is a literal separator. Matching this format exactly requires `%8ld` for each column, not `%ld` (which would left-align or not pad).

---

## Total row only for multiple files

```c
if (nfiles > 1)
    print_row(total, "total", flag_l, flag_w, flag_c, no_flag);
```

Real `wc` prints a `total` row only when more than one file is given. A single-file invocation never shows a total.

---

## Summary of edge cases handled

| Scenario | How it is handled |
|---|---|
| File not found | `fopen` fails → `strerror(errno)` to stderr → continue → exit 1 |
| Directory argument | `stat` + `S_ISDIR` check → "read: Is a directory" → continue → exit 1 |
| No files given | Reads from stdin |
| Multiple files | Accumulates totals; prints `total` row at end |
| Single file | No total row |
