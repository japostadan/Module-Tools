# JavaScript Implementation Notes — `ls`

This document explains the key decisions behind `ls.js`.

---

## Sorting: `localeCompare` with `toLowerCase`

```js
entries = fs.readdirSync(targetPath)
  .sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
```

JavaScript's default `Array.sort` is lexicographic by Unicode code point — uppercase before lowercase. To match macOS `ls` case-insensitive sorting, both strings are lowercased before comparison. `localeCompare` is used instead of `<`/`>` because it respects locale-specific collation rules for non-ASCII characters.

**Why not just `a.toLowerCase() < b.toLowerCase()`?**
Comparison operators on strings in JS return boolean, not a number. `Array.sort` expects a comparator returning a negative, zero, or positive number. `localeCompare` returns exactly that.

---

## `readdirSync` never returns `.` and `..`

Same as the Python version: Node.js `fs.readdirSync` omits `.` and `..`. When `-a` is active, they are printed manually as the first two entries.

---

## `osError` helper — gap for file paths

```js
} catch (err) {
  const msg = err.code === 'EACCES' ? 'Permission denied' : 'No such file or directory';
  process.stderr.write(`ls: ${targetPath}: ${msg}\n`);
  process.exit(1);
}
```

The error handler only maps `EACCES`. Everything else (including `ENOTDIR` — which fires when you pass a file path) falls through to "No such file or directory", which is wrong. Real `ls` with a file path does not error at all — it prints the path and exits 0. This is tracked in `error.md`. The fix is to check `fs.statSync(path).isFile()` before calling `readdirSync`.

---

## `console.log` vs `process.stdout.write`

```js
console.log('.');
console.log('..');
for (const entry of entries) console.log(entry);
```

`console.log` adds a newline. Since filenames never contain trailing newlines, this is safe. The choice between `console.log` and `process.stdout.write(entry + '\n')` is stylistic — both produce identical output for filenames.

---

## Summary of edge cases handled

| Scenario | How it is handled |
|---|---|
| Directory not found | `readdirSync` throws → error message → `process.exit(1)` |
| Permission denied | `EACCES` → "Permission denied" message |
| `-a` flag | `.` and `..` printed first, then sorted entries |
| Case-insensitive sort | `toLowerCase()` + `localeCompare` |
| File path instead of dir | Not handled — shows wrong error and exits 1 (tracked in `error.md`) |
