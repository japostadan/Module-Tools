/* Usage: ./ls [-1] [-a] [path]
 * Compile: gcc -o ls ls.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>

#define MAX_ENTRIES 1024

static int cmp_casefold(const void *a, const void *b) {
    return strcasecmp(*(const char **)a, *(const char **)b);
}

int main(int argc, char *argv[]) {
    int show_all = 0;
    const char *path = ".";

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-a") == 0) show_all = 1;
        else if (strcmp(argv[i], "-1") == 0) { /* default */ }
        else if (argv[i][0] != '-') path = argv[i];
    }

    DIR *dir = opendir(path);
    if (!dir) { perror(path); return 1; }

    char *entries[MAX_ENTRIES];
    int count = 0;
    struct dirent *entry;

    while ((entry = readdir(dir)) != NULL) {
        const char *name = entry->d_name;
        if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) continue;
        entries[count++] = strdup(name);
    }
    closedir(dir);

    qsort(entries, count, sizeof(char *), cmp_casefold);

    if (show_all) {
        puts(".");
        puts("..");
        for (int i = 0; i < count; i++) puts(entries[i]);
    } else {
        for (int i = 0; i < count; i++) {
            if (entries[i][0] != '.') puts(entries[i]);
        }
    }

    for (int i = 0; i < count; i++) free(entries[i]);
    return 0;
}
