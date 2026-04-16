/* Usage: ./ls [-1] [-a] [path]
 * Compile: gcc -Wall -Wextra -Werror -o ls ls.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <errno.h>

#define MAX_ENTRIES 1024

static int cmp_casefold(const void *a, const void *b) {
    return strcasecmp(*(const char *const *)a, *(const char *const *)b);
}

static void free_entries(char **entries, size_t count) {
    for (size_t i = 0; i < count; i++) free(entries[i]);
}

int main(int argc, char *argv[]) {
    int show_all = 0;
    const char *path = ".";

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-a") == 0)
			show_all = 1;
        else if (strcmp(argv[i], "-1") == 0);
        else if (argv[i][0] != '-')
			path = argv[i];
        else {
            fprintf(stderr, "ls: illegal option -- %c\n", argv[i][1]);
            fprintf(stderr, "usage: ls [-1a] [path]\n");
            return 1;
        }
    }

    DIR *dir = opendir(path);
    if (!dir) {
        fprintf(stderr, "ls: %s: %s\n", path, strerror(errno));
        return 1;
    }

    char *entries[MAX_ENTRIES];
    size_t count = 0;
    struct dirent *entry;

    while ((entry = readdir(dir)) != NULL) {
        const char *name = entry->d_name;
        if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) continue;

        if (count >= MAX_ENTRIES) {
            fprintf(stderr, "ls: too many entries (max %d)\n", MAX_ENTRIES);
            closedir(dir);
            free_entries(entries, count);
            return 1;
        }

        entries[count] = strdup(name);
        if (!entries[count]) {
            perror("ls: strdup");
            closedir(dir);
            free_entries(entries, count);
            return 1;
        }
        count++;
    }
    closedir(dir);

    qsort(entries, count, sizeof(char *), cmp_casefold);

    if (show_all) {
        puts(".");
        puts("..");
        for (size_t i = 0; i < count; i++) puts(entries[i]);
    } else {
        for (size_t i = 0; i < count; i++) {
            if (entries[i][0] != '.') puts(entries[i]);
        }
    }

    free_entries(entries, count);
    return 0;
}
