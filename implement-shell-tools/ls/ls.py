#!/usr/bin/env python3
import sys
import os


def main():
    args = sys.argv[1:]
    show_all = False
    path = '.'

    for arg in args:
        if arg == '-1':
            pass  # one-per-line is our only output mode
        elif arg == '-a':
            show_all = True
        elif not arg.startswith('-'):
            path = arg

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
                print(entry)


if __name__ == '__main__':
    main()
