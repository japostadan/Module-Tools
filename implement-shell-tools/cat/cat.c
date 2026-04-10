/* Usage: ./cat [-n] [-b] file1 [file2 ...]
 * Compile: gcc -o cat cat.c
 */
#include <stdio.h>
#include <string.h>
#include <errno.h>

static void process_stream(FILE *f, int flag_n, int flag_b) {
    int line_num = 0;
    char line[8192];
    while (fgets(line, sizeof(line), f)) {
        int is_blank = (line[0] == '\n');
        if (flag_b) {
            if (is_blank) {
                fputs(line, stdout);
            } else {
                line_num++;
                printf("%6d\t%s", line_num, line);
            }
        } else if (flag_n) {
            line_num++;
            printf("%6d\t%s", line_num, line);
        } else {
            fputs(line, stdout);
        }
    }
}

int main(int argc, char *argv[]) {
    int flag_n = 0, flag_b = 0;
    char *files[256];
    int nfiles = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-n") == 0)      flag_n = 1;
        else if (strcmp(argv[i], "-b") == 0) flag_b = 1;
        else files[nfiles++] = argv[i];
    }

    if (nfiles == 0) {
        process_stream(stdin, flag_n, flag_b);
        return 0;
    }

    int exit_code = 0;
    for (int i = 0; i < nfiles; i++) {
        FILE *f = fopen(files[i], "r");
        if (!f) {
            fprintf(stderr, "cat: %s: %s\n", files[i], strerror(errno));
            exit_code = 1;
            continue;
        }
        process_stream(f, flag_n, flag_b);
        fclose(f);
    }
    return exit_code;
}
