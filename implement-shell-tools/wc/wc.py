#!/usr/bin/env python3
import sys

USAGE = "usage: wc [-Lclmw] [file ...]"
KNOWN_FLAGS = set('Lclmw')


def count(content):
    """Return (lines, words, bytes) counts from binary content."""
    lines = content.count(b'\n')
    words = len(content.split())
    nbytes = len(content)
    return lines, words, nbytes


def print_row(lines, words, nbytes, label, flag_l, flag_w, flag_c):
    suffix = f" {label}" if label else ""
    if flag_l:
        print(f"{lines:8}{suffix}")
    elif flag_w:
        print(f"{words:8}{suffix}")
    elif flag_c:
        print(f"{nbytes:8}{suffix}")
    else:
        print(f"{lines:8}{words:8}{nbytes:8}{suffix}")


def parse_args(args):
    flag_l = False
    flag_w = False
    flag_c = False
    files = []

    for arg in args:
        if arg.startswith('-') and len(arg) > 1:
            for ch in arg[1:]:
                if ch == 'l':
                    flag_l = True
                elif ch == 'w':
                    flag_w = True
                elif ch == 'c':
                    flag_c = True
                elif ch not in KNOWN_FLAGS:
                    print(f"wc: illegal option -- {ch}", file=sys.stderr)
                    print(USAGE, file=sys.stderr)
                    sys.exit(1)
        else:
            files.append(arg)

    return flag_l, flag_w, flag_c, files


def main():
    flag_l, flag_w, flag_c, files = parse_args(sys.argv[1:])
    exit_code = 0

    if not files:
        content = sys.stdin.buffer.read()
        lines, words, nbytes = count(content)
        print_row(lines, words, nbytes, '', flag_l, flag_w, flag_c)
        sys.exit(0)

    total_lines = total_words = total_bytes = 0

    for filepath in files:
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            lines, words, nbytes = count(content)
            total_lines += lines
            total_words += words
            total_bytes += nbytes
            print_row(lines, words, nbytes, filepath, flag_l, flag_w, flag_c)
        except IsADirectoryError as e:
            print(f"wc: {filepath}: read: {e.strerror}", file=sys.stderr)
            exit_code = 1
        except OSError as e:
            print(f"wc: {filepath}: open: {e.strerror}", file=sys.stderr)
            exit_code = 1

    if len(files) > 1:
        print_row(total_lines, total_words, total_bytes, 'total', flag_l, flag_w, flag_c)

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
