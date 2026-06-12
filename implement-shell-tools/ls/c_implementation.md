# C Implementation Notes — `ls`

This document explains the key decisions behind `ls.c`: why each piece is written the way it is, and what would break if you changed it.

---

## Compile flags

```bash
gcc -Wall -Wextra -Werror -o ls ls.c
```

- `-Wall` — enables the most common warnings (unused variables, missing returns, etc.)
- `-Wextra` — enables additional warnings not covered by `-Wall` (sign-compare, missing field initializers, etc.)
- `-Werror` — turns every warning into a hard error, so the code cannot be built with known issues

The goal is to treat warnings as bugs at compile time, not runtime surprises.

---

## Comparator: `cmp_casefold`

```c
static int cmp_casefold(const void *a, const void *b) {
    return strcasecmp(*(const char *const *)a, *(const char *const *)b);
}
```

**Why `strcasecmp`?**
macOS `ls` sorts entries case-insensitively — `README.md` sorts alongside `readme.md`, not after `z`. The standard `strcmp` would sort uppercase letters before lowercase because `'A'` (65) < `'a'` (97) in ASCII.

**Why `const char *const *`?**
`qsort` passes each element as `const void *`. Each element in the array is a `char *` (a pointer to a string), so casting to `const char **` lets us dereference to get the string. The extra `const` before `*` means "the pointer itself is also const" — we're not modifying the pointer, only reading through it. This is the most accurate type and avoids a `-Wextra` warning about discarding const qualifiers.

**Why `static`?**
The function is only used inside this file. Marking it `static` restricts its linkage to this translation unit — it won't conflict with a `cmp_casefold` symbol in any other file if this code is ever compiled alongside other objects.

---

## Cleanup helper: `free_entries`

```c
static void free_entries(char **entries, size_t count) {
    for (size_t i = 0; i < count; i++) free(entries[i]);
}
```

There are three places in `main` that need to free the entry array: the too-many-entries error, the `strdup` failure, and the normal exit. Without this helper, each would need the same loop duplicated. Duplicated cleanup loops are a common source of bugs — one copy gets updated, the others don't.

The function takes `count` as a `size_t` to match the type used in `main`, avoiding a sign-compare warning.

---

## Entry storage: fixed array vs. dynamic allocation

```c
char *entries[MAX_ENTRIES];
size_t count = 0;
```

The array holds `char *` pointers — each slot points to a heap-allocated string from `strdup`. The array itself lives on the stack.

**Why a fixed array and not `malloc`?**
For the scope of this exercise (listing a directory with at most a few hundred entries), a fixed array is simpler and has no allocation overhead. The tradeoff is that it silently fails on directories with more than `MAX_ENTRIES` entries — but the bounds check (see below) turns that silent failure into an explicit error.

**Why `size_t count` and not `int`?**
`qsort`'s second parameter is `size_t`. Passing a signed `int` triggers a sign-compare warning under `-Wextra` because the compiler cannot guarantee that a negative value won't be implicitly converted to a large unsigned number. Using `size_t` throughout eliminates the mismatch.

---

## Bounds check before writing to the array

```c
if (count >= MAX_ENTRIES) {
    fprintf(stderr, "ls: too many entries (max %d)\n", MAX_ENTRIES);
    closedir(dir);
    free_entries(entries, count);
    return 1;
}
```

Without this, a directory with 1025 entries would write past the end of `entries` — a stack buffer overflow, which is undefined behavior and a potential security issue. The check ensures the write at `entries[count]` is always in bounds.

The `closedir` and `free_entries` calls before `return 1` are essential: resources allocated before the error must be released. Forgetting either is a resource leak.

---

## `strdup` NULL check

```c
entries[count] = strdup(name);
if (!entries[count]) {
    perror("ls: strdup");
    closedir(dir);
    free_entries(entries, count);
    return 1;
}
count++;
```

`strdup` returns `NULL` if the heap allocation fails. Storing `NULL` and continuing would cause `puts(NULL)` or `free(NULL)` — the former is undefined behavior (crash), the latter is safe but wrong.

`count++` is placed *after* the NULL check so that a failed `strdup` does not count as a stored entry. If it incremented first and then the check freed `entries[count]`, it would free one slot that was never written.

---

## Unknown flag handling

```c
else {
    fprintf(stderr, "ls: illegal option -- %c\n", argv[i][1]);
    fprintf(stderr, "usage: ls [-1a] [path]\n");
    return 1;
}
```

The original code silently ignored unknown flags — `./ls -z` would just list the directory as if `-z` were not passed. The real `ls` rejects unknown flags with an error message. Matching this behavior is important: silently ignoring input hides typos and incorrect usage.

The error message format (`illegal option -- x`) matches the macOS `ls` convention exactly.

---

## Output: `puts` vs `printf`

```c
puts(entries[i]);
```

`puts(s)` is equivalent to `printf("%s\n", s)` but simpler and slightly faster — it doesn't parse a format string. Since all we need is to print a string and a newline, `puts` is the right tool.

---

## Error output: `stderr` vs `stdout`

```c
fprintf(stderr, "ls: %s: %s\n", path, strerror(errno));
```

Diagnostic messages go to `stderr` so they don't pollute the output when `ls` is used in a pipeline. Writing errors to `stdout` would corrupt the output of `ls | grep foo` with error text mixed into the entries.

---

## Summary of edge cases handled

| Scenario | How it is handled |
|---|---|
| Path does not exist | `opendir` fails → print `strerror(errno)` → exit 1 |
| Path is a file, not a directory | `opendir` fails with `ENOTDIR` → same path |
| More than 1024 entries | Bounds check → error message → cleanup → exit 1 |
| Heap allocation fails (`strdup`) | NULL check → `perror` → cleanup → exit 1 |
| Unknown flag (e.g. `-z`) | Print "illegal option" message → exit 1 |
