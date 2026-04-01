#!/usr/bin/env node
// Usage: node ls.js [-1] [-a] [path]
const fs = require('fs');

const args = process.argv.slice(2);
let showAll = false;
let targetPath = '.';

for (const arg of args) {
  if (arg === '-a') showAll = true;
  else if (arg === '-1') { /* one-per-line is our only output mode */ }
  else if (!arg.startsWith('-')) targetPath = arg;
}

const entries = fs.readdirSync(targetPath)
  .sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));

if (showAll) {
  console.log('.');
  console.log('..');
  for (const entry of entries) console.log(entry);
} else {
  for (const entry of entries) {
    if (!entry.startsWith('.')) console.log(entry);
  }
}
