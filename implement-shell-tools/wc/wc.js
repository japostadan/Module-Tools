#!/usr/bin/env node
// Usage: node wc.js [-l] [-w] [-c] file1 [file2 ...]
const fs = require('fs');

const args = process.argv.slice(2);
let flagL = false;
let flagW = false;
let flagC = false;
const files = [];

for (const arg of args) {
  if (arg === '-l') flagL = true;
  else if (arg === '-w') flagW = true;
  else if (arg === '-c') flagC = true;
  else files.push(arg);
}

const noFlag = !(flagL || flagW || flagC);

function osError(err) {
  if (err.code === 'EACCES') return 'Permission denied';
  if (err.code === 'ENOENT') return 'No such file or directory';
  return err.message;
}

function countBytes(buf) {
  const lines = Array.from(buf).filter(b => b === 10).length;
  const text = buf.toString('utf8').trim();
  const words = text === '' ? 0 : text.split(/\s+/).length;
  const chars = buf.length;
  return { lines, words, chars };
}

function countString(str) {
  const lines = (str.match(/\n/g) || []).length;
  const text = str.trim();
  const words = text === '' ? 0 : text.split(/\s+/).length;
  const chars = str.length;
  return { lines, words, chars };
}

function printRow(lines, words, chars, label) {
  const suffix = label ? ` ${label}` : '';
  if (noFlag) {
    process.stdout.write(
      `${String(lines).padStart(8)}${String(words).padStart(8)}${String(chars).padStart(8)}${suffix}\n`
    );
  } else if (flagL) {
    process.stdout.write(`${String(lines).padStart(8)}${suffix}\n`);
  } else if (flagW) {
    process.stdout.write(`${String(words).padStart(8)}${suffix}\n`);
  } else if (flagC) {
    process.stdout.write(`${String(chars).padStart(8)}${suffix}\n`);
  }
}

if (files.length === 0) {
  let content = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => { content += chunk; });
  process.stdin.on('end', () => {
    const { lines, words, chars } = countString(content);
    printRow(lines, words, chars, '');
  });
} else {
  let exitCode = 0;
  let totalLines = 0, totalWords = 0, totalChars = 0;

  for (const filepath of files) {
    try {
      const buf = fs.readFileSync(filepath);
      const { lines, words, chars } = countBytes(buf);
      totalLines += lines;
      totalWords += words;
      totalChars += chars;
      printRow(lines, words, chars, filepath);
    } catch (err) {
      process.stderr.write(`wc: ${filepath}: open: ${osError(err)}\n`);
      exitCode = 1;
    }
  }

  if (files.length > 1) printRow(totalLines, totalWords, totalChars, 'total');
  process.exit(exitCode);
}
