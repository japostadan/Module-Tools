#!/usr/bin/env python3
import sys
import os


def main():
    args = sys.argv[1:]
    show_all = False
    show_one_per_line = False
    path = '.'

    for arg in args:
        if arg == '-1':
            show_one_per_line = True
        elif arg == '-a':
            show_all = True
        elif not arg.startswith('-'):
            path = arg
        else:
            print(f"ls: invalid option -- '{arg}'", file=sys.stderr)
            sys.exit(1)

    try:
        entries = sorted(os.listdir(path), key=str.casefold)
    except OSError as e:
        print(f"ls: {path}: {e.strerror}", file=sys.stderr)
        sys.exit(1)

    if show_all:
        print('.')
        print('..')
        for entry in entries:
            print(entry)
    else:
        for entry in entries:
            if not entry.startswith('.'):
                if show_one_per_line:
                    print(entry)
                else:
                    print(entry, end='\t')

if __name__ == '__main__':
    main()
