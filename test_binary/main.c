#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define STRING_SIZE 32

typedef struct {
    int randomInt;
    float randomFloat;
    char randomString[STRING_SIZE];
} Data;

int asd(Data data) {
    printf("Address: %p\n", (void*)&data);
    printf("    Int: %d\n", data.randomInt);
    printf("  Float: %.2f\n", data.randomFloat);
    printf(" String: %s\n", data.randomString);
    
    return 0;
}

int main() {
    srand((unsigned int)time(NULL));

    Data data;

    data.randomInt = rand() % 1000;
    data.randomFloat = (float)rand() / RAND_MAX * 100.0f;

    const char charset[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    for (int i = 0; i < STRING_SIZE - 1; i++) {
        data.randomString[i] = charset[rand() % (sizeof(charset) - 1)];
    }
    data.randomString[STRING_SIZE - 1] = '\0';

    asd(data);
    printf("Press ENTER to exit...\n");
    getchar();

    return 0;
}

