# C Implementation Notes — `cat`

This document explains the key decisions behind `cat.c`: why each piece is written the way it is, and what would break if you changed it.

---

## Compile flags

```bash
gcc -Wall -Wextra -Werror -o cat cat.c
```

Same rationale as the other tools: `-Werror` turns every warning into a compile failure, forcing issues to be resolved before the binary is produced.

---

## `process_stream` — the core loop

```c
static void process_stream(FILE *f, int flag_n, int flag_b, int *line_num) {
    char *line = NULL;
    size_t capacity = 0;
    ssize_t len;

    while ((len = getline(&line, &capacity, f)) != -1) {
        ...
        fputs(line, stdout);
    }
    free(line);
}
```

**Why `getline` instead of `fgets`?**
`fgets` requires a fixed-size buffer — you have to guess the maximum line length. `getline` allocates exactly as much memory as needed and grows the buffer if the line is longer. It's the right tool when you don't know or want to assume a line length limit.

**Why `NULL` and `0` for the initial buffer?**
When you pass `line = NULL` and `capacity = 0`, `getline` does the first allocation itself. You don't need a `malloc` before the loop.

**Why `fputs` instead of `printf`?**
`printf("%s", line)` parses a format string on every call. `fputs` just writes the string — no format parsing, no risk of format string bugs if `line` happened to contain `%` characters.

**Why pass `line_num` as a pointer?**
`-b` (number non-blank lines) needs to share a counter between iterations — if a blank line is skipped, the counter must not increment. A pointer allows the function to update the caller's variable directly. However, this also means the caller must reset the counter to `0` before each new file, or numbers will continue across files (see below).

---

## Line counter reset per file

```c
line_num = 0;
process_stream(f, flag_n, flag_b, &line_num);
```

Real `cat -n` resets numbering for each file — file 2 always starts at line 1, regardless of how many lines file 1 had. The counter is reset to `0` in the file loop before each call to `process_stream`. Without this reset, the counter would be cumulative across files.

---

## `-b` takes precedence over `-n`

```c
if (strcmp(argv[i], "-b") == 0) {
    flag_b = 1;
    flag_n = 0;
} else if (strcmp(argv[i], "-n") == 0) {
    if (!flag_b)
        flag_n = 1;
}
```

On macOS, passing both `-n` and `-b` together: `-b` wins. The code enforces this in two ways:
- Setting `-b` explicitly clears `flag_n`
- Setting `-n` is silently ignored if `-b` is already active

---

## Blank line detection

```c
int is_blank = (len == 1 && line[0] == '\n');
```

`getline` includes the newline in the buffer. A line that is only a newline character has `len == 1`. This is the exact same condition the real `cat -b` uses to decide whether to number a line. Checking `strlen(line) == 1` would also work but is an O(n) scan; checking `len` (already known from `getline`) is O(1).

---

## Stdin fallback

```c
if (!had_input) {
    process_stream(stdin, flag_n, flag_b, &line_num);
}
```

Real `cat` with no file arguments reads from stdin. The `had_input` flag tracks whether any file argument was seen. A `-` argument is also treated as stdin (matching real `cat` behavior).

---

## Error handling

```c
f = fopen(argv[i], "r");
if (!f) {
    fprintf(stderr, "cat: %s: %s\n", argv[i], strerror(errno));
    exit_code = 1;
    continue;
}
```

Real `cat` does not stop on a bad file — it prints the error and moves on to the next argument. The `continue` and non-zero `exit_code` (returned at the end) match this behavior. Errors go to `stderr` so they don't corrupt the file content being written to `stdout`.

---

## Summary of edge cases handled

| Scenario | How it is handled |
|---|---|
| File not found | `fopen` fails → print `strerror(errno)` to stderr → continue to next file → exit 1 |
| Mixed good/bad files | Error on bad file, content of good files still printed in order |
| No arguments | Falls back to reading stdin |
| `-` argument | Treated as stdin |
| `-b` and `-n` together | `-b` wins; `-n` is cleared |
| Line counter across files | Reset to 0 before each file |
