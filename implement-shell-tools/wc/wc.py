#!/usr/bin/env python3
import sys


def count_bytes(content):
    lines = content.count(b'\n')
    words = len(content.split())
    chars = len(content)
    return lines, words, chars


def print_row(lines, words, chars, label, flag_l, flag_w, flag_c, no_flag):
    suffix = f" {label}" if label else ""
    if no_flag:
        print(f"{lines:8}{words:8}{chars:8}{suffix}")
    elif flag_l:
        print(f"{lines:8}{suffix}")
    elif flag_w:
        print(f"{words:8}{suffix}")
    elif flag_c:
        print(f"{chars:8}{suffix}")


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
    exit_code = 0

    if not files:
        content = sys.stdin.buffer.read()
        lines, words, chars = count_bytes(content)
        print_row(lines, words, chars, '', flag_l, flag_w, flag_c, no_flag)
    else:
        total_lines = total_words = total_chars = 0
        counted = []
        for filepath in files:
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                lines, words, chars = count_bytes(content)
                total_lines += lines
                total_words += words
                total_chars += chars
                counted.append((lines, words, chars, filepath))
                print_row(lines, words, chars, filepath, flag_l, flag_w, flag_c, no_flag)
            except OSError as e:
                print(f"wc: {filepath}: open: {e.strerror}", file=sys.stderr)
                exit_code = 1

        if len(files) > 1:
            print_row(total_lines, total_words, total_chars, 'total',
                      flag_l, flag_w, flag_c, no_flag)

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
