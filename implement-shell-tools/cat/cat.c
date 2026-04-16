#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>

static void process_stream(FILE *f, int flag_n, int flag_b, int *line_num) {
    char *line = NULL;
    size_t capacity = 0;
    ssize_t len;

    while ((len = getline(&line, &capacity, f)) != -1) {
        int is_blank = (len == 1 && line[0] == '\n');

        if (flag_b) {
            if (!is_blank) {
                (*line_num)++;
                fprintf(stdout, "%6d\t", *line_num);
            }
        } else if (flag_n) {
            (*line_num)++;
            fprintf(stdout, "%6d\t", *line_num);
        }

        fputs(line, stdout);
    }

    free(line);
}

int main(int argc, char *argv[]) {
    int flag_n = 0, flag_b = 0;
    int exit_code = 0;
    int line_num = 0;
    int had_input = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-b") == 0) {
            flag_b = 1;
            flag_n = 0;
        } else if (strcmp(argv[i], "-n") == 0) {
            if (!flag_b)
                flag_n = 1;
        } else {
            had_input = 1;

            FILE *f;

            if (strcmp(argv[i], "-") == 0) {
                f = stdin;
            } else {
                f = fopen(argv[i], "r");
                if (!f) {
                    fprintf(stderr, "cat: %s: %s\n", argv[i], strerror(errno));
                    exit_code = 1;
                    continue;
                }
            }

            line_num = 0;
            process_stream(f, flag_n, flag_b, &line_num);

            if (f != stdin)
                fclose(f);
        }
    }

    if (!had_input) {
        process_stream(stdin, flag_n, flag_b, &line_num);
    }

    return exit_code;
}
