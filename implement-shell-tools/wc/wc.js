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

function countFile(filepath) {
  const content = fs.readFileSync(filepath);
  const lines = Array.from(content).filter(b => b === 10).length;
  const text = content.toString('utf8').trim();
  const words = text === '' ? 0 : text.split(/\s+/).length;
  const chars = content.length;
  return { lines, words, chars };
}

function printRow(lines, words, chars, label) {
  if (noFlag) {
    process.stdout.write(
      `${String(lines).padStart(8)}${String(words).padStart(8)}${String(chars).padStart(8)} ${label}\n`
    );
  } else if (flagL) {
    process.stdout.write(`${String(lines).padStart(8)} ${label}\n`);
  } else if (flagW) {
    process.stdout.write(`${String(words).padStart(8)} ${label}\n`);
  } else if (flagC) {
    process.stdout.write(`${String(chars).padStart(8)} ${label}\n`);
  }
}

let totalLines = 0, totalWords = 0, totalChars = 0;

for (const filepath of files) {
  const { lines, words, chars } = countFile(filepath);
  totalLines += lines;
  totalWords += words;
  totalChars += chars;
  printRow(lines, words, chars, filepath);
}

if (files.length > 1) {
  printRow(totalLines, totalWords, totalChars, 'total');
}
