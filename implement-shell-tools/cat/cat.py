#!/usr/bin/env python3
import sys


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

    for filepath in files:
        line_num = 0
        with open(filepath) as f:
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


if __name__ == '__main__':
    main()
