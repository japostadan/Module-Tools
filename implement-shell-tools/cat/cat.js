#!/usr/bin/env node
// Usage: node cat.js [-n] [-b] file1 [file2 ...]
const fs = require('fs');

const args = process.argv.slice(2);
let flagN = false;
let flagB = false;
const files = [];

for (const arg of args) {
  if (arg === '-n') flagN = true;
  else if (arg === '-b') flagB = true;
  else files.push(arg);
}

for (const filepath of files) {
  const content = fs.readFileSync(filepath, 'utf8');
  const lines = content.split('\n');
  // If file ends with \n, split produces a trailing '' — skip it
  if (lines[lines.length - 1] === '') lines.pop();

  let lineNum = 0;
  for (const line of lines) {
    if (flagB) {
      if (line === '') {
        process.stdout.write('\n');
      } else {
        lineNum++;
        process.stdout.write(`${String(lineNum).padStart(6)}\t${line}\n`);
      }
    } else if (flagN) {
      lineNum++;
      process.stdout.write(`${String(lineNum).padStart(6)}\t${line}\n`);
    } else {
      process.stdout.write(line + '\n');
    }
  }
}
