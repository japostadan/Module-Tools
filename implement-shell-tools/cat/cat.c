/* Usage: ./cat [-n] [-b] file1 [file2 ...]
 * Compile: gcc -o cat cat.c
 */
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    int flag_n = 0, flag_b = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-n") == 0) flag_n = 1;
        else if (strcmp(argv[i], "-b") == 0) flag_b = 1;
    }

    for (int i = 1; i < argc; i++) {
        if (argv[i][0] == '-') continue;

        FILE *f = fopen(argv[i], "r");
        if (!f) { perror(argv[i]); return 1; }

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
        fclose(f);
    }
    return 0;
}
