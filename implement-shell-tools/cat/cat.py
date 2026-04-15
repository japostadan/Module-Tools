#!/usr/bin/env python3
import sys

USAGE = "usage: cat [-belnstuv] [file ...]"
KNOWN_FLAGS = set('belnstuv')


def print_lines(f, flag_n, flag_b):
    """Write lines from file-like object f to stdout, with optional numbering."""
    line_num = 0
    for line in f:
        is_blank = line.rstrip('\n') == ''
        if flag_b and not is_blank:
            line_num += 1
            sys.stdout.write(f"{line_num:6}\t{line}")
        elif flag_n and not flag_b:
            line_num += 1
            sys.stdout.write(f"{line_num:6}\t{line}")
        else:
            sys.stdout.write(line)


def parse_args(args):
    flag_n = False
    flag_b = False
    files = []

    for arg in args:
        if arg.startswith('-') and len(arg) > 1:
            for ch in arg[1:]:
                if ch == 'n':
                    flag_n = True
                elif ch == 'b':
                    flag_b = True
                elif ch not in KNOWN_FLAGS:
                    print(f"cat: illegal option -- {ch}", file=sys.stderr)
                    print(USAGE, file=sys.stderr)
                    sys.exit(1)
        else:
            files.append(arg)

    return flag_n, flag_b, files


def main():
    flag_n, flag_b, files = parse_args(sys.argv[1:])
    exit_code = 0

    try:
        if not files:
            print_lines(sys.stdin, flag_n, flag_b)
        else:
            for filepath in files:
                try:
                    with open(filepath) as f:
                        print_lines(f, flag_n, flag_b)
                    sys.stdout.flush()
                except OSError as e:
                    sys.stdout.flush()
                    print(f"cat: {filepath}: {e.strerror}", file=sys.stderr)
                    exit_code = 1
    except KeyboardInterrupt:
        exit_code = 1

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
