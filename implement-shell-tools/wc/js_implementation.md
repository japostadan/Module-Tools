# JavaScript Implementation Notes — `wc`

This document explains the key decisions behind `wc.js`.

---

## Two counting functions: `countBytes` and `countString`

```js
function countBytes(buf) { ... }   // used for files (Buffer)
function countString(str) { ... }  // used for stdin (string)
```

Files are read with `fs.readFileSync(filepath)` — no encoding argument — which returns a `Buffer` (raw bytes). Stdin is read as a string (UTF-8). Rather than convert between types, two separate functions handle each case.

**Why does this matter?**
`buf.length` on a `Buffer` is the byte count. `str.length` on a string is the character count (UTF-16 code units). For ASCII files they're identical, but for non-ASCII content they diverge. Using `Buffer` for files ensures `chars` is always a byte count.

---

## `countBytes` — Buffer-based counting

```js
function countBytes(buf) {
  const lines = Array.from(buf).filter(b => b === 10).length;
  const text = buf.toString('utf8').trim();
  const words = text === '' ? 0 : text.split(/\s+/).length;
  const chars = buf.length;
}
```

**Lines:** Byte `10` is the ASCII code for `\n`. `Array.from(buf)` converts the buffer to an array of byte values, then filters for newlines. This is direct byte counting — no string conversion needed.

**Words:** The buffer is decoded to a string for word splitting. `split(/\s+/)` splits on any whitespace sequence. `.trim()` first removes leading/trailing whitespace so a file that starts or ends with a space doesn't produce empty tokens at the boundaries. The empty-string check prevents `''.split(/\s+/)` from returning `['']` (length 1) for an empty file.

**Chars:** `buf.length` is the byte count.

---

## Directory error message (known limitation)

```js
process.stderr.write(`wc: ${filepath}: open: ${osError(err)}\n`);
```

When a directory is passed, Node.js throws with `err.code === 'EISDIR'`. The `osError` helper does not map `EISDIR`, so it falls through to `err.message` — a raw Node.js error string that does not match the macOS format. The correct output would be `read: Is a directory`. This is tracked in `error.md`.

---

## Stdin: event-driven accumulation

```js
process.stdin.on('data', chunk => { content += chunk; });
process.stdin.on('end', () => {
  const { lines, words, chars } = countString(content);
  printRow(lines, words, chars, '');
});
```

Node.js stdin is a readable stream. Data arrives in chunks via `data` events. The implementation accumulates all chunks into a string and processes it when the `end` event fires. This is the correct pattern for consuming stdin in Node.js — you cannot read synchronously from stdin without special setup.

---

## `printRow` — padStart for alignment

```js
process.stdout.write(
  `${String(lines).padStart(8)}${String(words).padStart(8)}${String(chars).padStart(8)}${suffix}\n`
);
```

JavaScript doesn't have printf-style format specifiers. `padStart(8)` right-pads a string to at least 8 characters, equivalent to C's `%8ld`. `String(n)` converts the number to a string first, since `padStart` is a string method.

---

## Total row for multiple files

```js
if (files.length > 1) printRow(totalLines, totalWords, totalChars, 'total');
```

Same rule as the C and Python versions: total is only printed when more than one file was given.

---

## Summary of edge cases handled

| Scenario | How it is handled |
|---|---|
| File not found | `readFileSync` throws → `osError` maps `ENOENT` → printed to stderr |
| Directory argument | `readFileSync` throws `EISDIR` → wrong message (tracked in `error.md`) |
| No files given | Stdin via event-driven accumulation |
| Byte vs character count | `Buffer` for files ensures `buf.length` = bytes |
| Multiple files | Accumulates totals; prints `total` row |
