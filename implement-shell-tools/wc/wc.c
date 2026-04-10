/* Usage: ./wc [-l] [-w] [-c] file1 [file2 ...]
 * Compile: gcc -o wc wc.c
 */
#include <stdio.h>
#include <string.h>
#include <errno.h>

typedef struct { long lines, words, chars; } Counts;

static Counts count_stream(FILE *f) {
    Counts c = {0, 0, 0};
    int ch, in_word = 0;
    while ((ch = fgetc(f)) != EOF) {
        c.chars++;
        if (ch == '\n') c.lines++;
        if (ch == ' ' || ch == '\t' || ch == '\n' || ch == '\r') {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            c.words++;
        }
    }
    return c;
}

static void print_row(Counts c, const char *label,
                      int flag_l, int flag_w, int flag_c, int no_flag) {
    if (no_flag) {
        if (label && *label)
            printf("%8ld%8ld%8ld %s\n", c.lines, c.words, c.chars, label);
        else
            printf("%8ld%8ld%8ld\n", c.lines, c.words, c.chars);
    } else if (flag_l) {
        if (label && *label) printf("%8ld %s\n", c.lines, label);
        else printf("%8ld\n", c.lines);
    } else if (flag_w) {
        if (label && *label) printf("%8ld %s\n", c.words, label);
        else printf("%8ld\n", c.words);
    } else if (flag_c) {
        if (label && *label) printf("%8ld %s\n", c.chars, label);
        else printf("%8ld\n", c.chars);
    }
}

int main(int argc, char *argv[]) {
    int flag_l = 0, flag_w = 0, flag_c = 0;
    char *files[256];
    int nfiles = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-l") == 0)      flag_l = 1;
        else if (strcmp(argv[i], "-w") == 0) flag_w = 1;
        else if (strcmp(argv[i], "-c") == 0) flag_c = 1;
        else files[nfiles++] = argv[i];
    }

    int no_flag = !(flag_l || flag_w || flag_c);

    if (nfiles == 0) {
        Counts c = count_stream(stdin);
        print_row(c, "", flag_l, flag_w, flag_c, no_flag);
        return 0;
    }

    int exit_code = 0;
    Counts total = {0, 0, 0};

    for (int i = 0; i < nfiles; i++) {
        FILE *f = fopen(files[i], "rb");
        if (!f) {
            fprintf(stderr, "wc: %s: open: %s\n", files[i], strerror(errno));
            exit_code = 1;
            continue;
        }
        Counts c = count_stream(f);
        fclose(f);
        total.lines += c.lines;
        total.words += c.words;
        total.chars += c.chars;
        print_row(c, files[i], flag_l, flag_w, flag_c, no_flag);
    }

    if (nfiles > 1)
        print_row(total, "total", flag_l, flag_w, flag_c, no_flag);

    return exit_code;
}
