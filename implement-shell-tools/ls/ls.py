#!/usr/bin/env python3
import sys
import os

USAGE = "usage: ls [-@ABCFGHILOPRSTUWXabcdefghiklmnopqrstuvwxy1%,] [--color=when] [-D format] [file ...]"
KNOWN_FLAGS = set('1a')


def parse_args(args):
    show_all = False
    one_per_line = False
    path = '.'

    for arg in args:
        if arg.startswith('-') and len(arg) > 1:
            for ch in arg[1:]:
                if ch == '1':
                    one_per_line = True
                elif ch == 'a':
                    show_all = True
                elif ch not in KNOWN_FLAGS:
                    print(f"ls: invalid option -- {ch}", file=sys.stderr)
                    print(USAGE, file=sys.stderr)
                    sys.exit(1)
        else:
            path = arg

    return show_all, one_per_line, path


def print_entry(name, one_per_line):
    if one_per_line:
        print(name)
    else:
        print(name, end='\t')


def main():
    show_all, one_per_line, path = parse_args(sys.argv[1:])

    if os.path.isfile(path):
        print(path)
        sys.exit(0)

    try:
        entries = sorted(os.listdir(path), key=str.casefold)
    except OSError as e:
        print(f"ls: {path}: {e.strerror}", file=sys.stderr)
        sys.exit(1)

    if show_all:
        all_entries = entries + ['.','..']
        for entry in sorted(all_entries):
            print_entry(entry, one_per_line)
    else:
        for entry in entries:
            if not entry.startswith('.'):
                print_entry(entry, one_per_line)


if __name__ == '__main__':
    main()
