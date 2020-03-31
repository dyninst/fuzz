all: fuzz pty_cross_platform

fuzz: fuzz.c
	gcc fuzz.c -o fuzz

pty_cross_platform: pty_cross_platform.c
	gcc pty_cross_platform.c -o pty_cross_platform

clean:
	rm ./fuzz ./pty_cross_platform
