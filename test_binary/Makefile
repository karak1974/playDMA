CC = x86_64-w64-mingw32-gcc
TARGET = testbinary.exe
SRC = main.c
CFLAGS = -Wall -Wextra -O2
LDFLAGS = -static

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(TARGET)

.PHONY: all clean

