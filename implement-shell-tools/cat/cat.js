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

function osError(err) {
  if (err.code === 'EACCES') return 'Permission denied';
  if (err.code === 'ENOENT') return 'No such file or directory';
  return err.message;
}

function processContent(content) {
  const lines = content.split('\n');
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

if (files.length === 0) {
  let content = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => { content += chunk; });
  process.stdin.on('end', () => { processContent(content); });
} else {
  let exitCode = 0;
  for (const filepath of files) {
    try {
      const content = fs.readFileSync(filepath, 'utf8');
      processContent(content);
    } catch (err) {
      process.stderr.write(`cat: ${filepath}: ${osError(err)}\n`);
      exitCode = 1;
    }
  }
  process.exit(exitCode);
}
