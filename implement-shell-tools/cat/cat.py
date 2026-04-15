#!/usr/bin/env python3
import sys


def process_lines(f, flag_n, flag_b):
    line_num = 0
    for line in f:
        if flag_b:
            if line.rstrip('\n') == '':
                sys.stdout.write(line)
            else:
                line_num += 1
                sys.stdout.write(f"{line_num:6}\t{line}")
        elif flag_n:
            line_num += 1
            sys.stdout.write(f"{line_num:6}\t{line}")
        else:
            sys.stdout.write(line)


def main():
    args = sys.argv[1:]
    flag_n = False
    flag_b = False
    files = []

    for arg in args:
        if arg == '-n':
            flag_n = True
        elif arg == '-b':
            flag_b = True
        else:
            files.append(arg)
    exit_code = 0

    try: 
        if not files:
            process_lines(sys.stdin, flag_n, flag_b)
        else:
            for filepath in files:
                try:
                    with open(filepath) as f:
                        process_lines(f, flag_n, flag_b)
                except OSError as e:
                    print(f"cat: {filepath}: {e.strerror}", file=sys.stderr)
                    exit_code = 1
    except KeyboardInterrupt:
        exit_code = 1

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
