#!/usr/bin/env python3
import sys


def count_file(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
    lines = content.count(b'\n')
    words = len(content.split())
    chars = len(content)
    return lines, words, chars


def main():
    args = sys.argv[1:]
    flag_l = False
    flag_w = False
    flag_c = False
    files = []

    for arg in args:
        if arg == '-l':
            flag_l = True
        elif arg == '-w':
            flag_w = True
        elif arg == '-c':
            flag_c = True
        else:
            files.append(arg)

    no_flag = not (flag_l or flag_w or flag_c)

    total_lines = total_words = total_chars = 0
    results = []

    for filepath in files:
        lines, words, chars = count_file(filepath)
        total_lines += lines
        total_words += words
        total_chars += chars
        results.append((lines, words, chars, filepath))

    for lines, words, chars, filepath in results:
        if no_flag:
            print(f"{lines:8}{words:8}{chars:8} {filepath}")
        elif flag_l:
            print(f"{lines:8} {filepath}")
        elif flag_w:
            print(f"{words:8} {filepath}")
        elif flag_c:
            print(f"{chars:8} {filepath}")

    if len(files) > 1:
        if no_flag:
            print(f"{total_lines:8}{total_words:8}{total_chars:8} total")
        elif flag_l:
            print(f"{total_lines:8} total")
        elif flag_w:
            print(f"{total_words:8} total")
        elif flag_c:
            print(f"{total_chars:8} total")


if __name__ == '__main__':
    main()
