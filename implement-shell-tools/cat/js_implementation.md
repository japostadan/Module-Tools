# JavaScript Implementation Notes — `cat`

This document explains the key decisions behind `cat.js`.

---

## File reading strategy: `readFileSync`

```js
const content = fs.readFileSync(filepath, 'utf8');
processContent(content);
```

The entire file is read into a string at once, then processed. This differs from the C and Python implementations which read line-by-line. It works for the test files but would be a problem for very large files (the entire file lives in memory at once). For a learning exercise matching small sample files, it is the simplest approach.

---

## `processContent` — line splitting

```js
const lines = content.split('\n');
if (lines[lines.length - 1] === '') lines.pop();
```

`split('\n')` produces an extra empty string at the end when the file ends with a newline (which all well-formed text files do). The `.pop()` removes that trailing empty entry so it is not printed as a blank line.

**Why not use `splitLines` or a regex?**
`split('\n')` is the simplest and most predictable approach for Unix line endings. The extra empty-string removal is the only edge case.

---

## Line counter reset per file

```js
let lineNum = 0;
```

`lineNum` is declared inside `processContent`, so it is always `0` at the start of each file. The counter reset is automatic from JavaScript's function scope — unlike a C pointer that persists across calls.

---

## `osError` helper

```js
function osError(err) {
  if (err.code === 'EACCES') return 'Permission denied';
  if (err.code === 'ENOENT') return 'No such file or directory';
  return err.message;
}
```

Node.js `Error` objects for file system errors include a `.code` property (e.g. `'ENOENT'`) and a `.message` string (e.g. `"ENOENT: no such file or directory, open 'x.txt'"`). The raw `.message` contains the file path and error code — not what real `cat` would print. The helper maps known codes to clean strings that match the macOS `strerror` output.

---

## Stdin handling

```js
if (files.length === 0) {
  let content = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => { content += chunk; });
  process.stdin.on('end', () => { processContent(content); });
}
```

Node.js I/O is event-driven. Unlike Python where `sys.stdin` is a synchronous iterator, stdin in Node.js emits `data` events as chunks arrive. The implementation accumulates all chunks into `content` and processes them when the `end` event fires. This is the correct asynchronous pattern for Node.js.

---

## `process.stdout.write` vs `console.log`

```js
process.stdout.write(`${String(lineNum).padStart(6)}\t${line}\n`);
```

`console.log` adds a newline automatically. Using `process.stdout.write` gives explicit control over what is written, including the exact newline character. This prevents double-newlines and is consistent with how the other tools write output.

---

## Summary of edge cases handled

| Scenario | How it is handled |
|---|---|
| File not found | `readFileSync` throws → `osError` maps code → printed to stderr → continue |
| No arguments | Collects stdin via event listeners |
| Trailing newline | `split('\n')` + `pop()` removes empty trailing entry |
| Line counter per file | Automatic — `lineNum` is local to each `processContent` call |
