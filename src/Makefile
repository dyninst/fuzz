all: fuzz pty

fuzz: fuzz.c
	gcc fuzz.c -o fuzz

pty: ptyjig_cross_platform.c
	gcc ptyjig_cross_platform.c -o pty

clean:
	rm ./fuzz ./pty
