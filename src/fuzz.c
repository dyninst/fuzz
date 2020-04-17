/* Copyright (c) 1989 Lars Fredriksen, Bryan So, Barton Miller
 * All rights reserved
 *  
 * This software is furnished under the condition that it may not
 * be provided or otherwise made available to, or used by, any
 * other person.  No title to or ownership of the software is
 * hereby transferred.
 *
 * Any use of this software must include the above copyright notice.
 *
 */

/*-
 *  Fuzz generator
 *
 *  Usage: fuzz [-0] [-a] [-d delay] [-o file] [-r file] [-l [lll]] 
 *              [-p] [-s sss] [-e epilog] [-x] [-m mmm] [n]
 *
 *  Generate n random characters to output.
 *
 *  Options:
 *
 *      n    Length of output, usually in byte. For -l, in # of strings.
 *
 *     -0    NULL (0 byte) characters included
 *
 *     -a    all ASCII character (default)
 *
 *     -d delay
 *           Delay for "delay" seconds between characters
 *
 *     -o file
 *           Record characters in "file"
 *
 *     -r file
 *           Replay characters in "file"
 *
 *     -l    random length LF terminated strings (lll max. default 255)
 *
 *     -p    printable ASCII only
 *
 *     -s    use sss as random seed
 *
 *     -e    send "epilog" after all random characters
 *
 *     -x    print the random seed as the first line
 *     
 *     -m    use mmm as modulus when generating random seed, i.e., the seed
 *           will be number from 0 to mmm-1
 *
 *  Defaults:
 *           fuzz -a 
 *           
 *
 *  Authors:
 *
 *  	Lars Fredriksen, Bryan So
 *
 *  Updated by:
 *
 *  	Bart Miller, Mengxiao Zhang, Emma He
 */

static char *progname = "fuzz";

#define DEBUG_off

#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <ctype.h>
#include <time.h>
#include <ctype.h>

#define SWITCH '-'

/*
 * Global flags 
 */
int     flag0 = 0;
int     flaga = 1;		/* 0 if flagp */
unsigned flagd = 0;
int     flagl = 0;
int     flags = 0;
int     flage = 0;
int     seed = 0;
int     flagn = 0;
int     flagx = 0;
int     flago = 0;
int     flagr = 0;
int     length = 0;
int     flagm = 0;
int     modulus = 0;
char    epilog[1024];
char   *infile, *outfile;
FILE   *in, *out;

void usage();
void init();
void replay();
void fuzz();
void putch(int i);
void fuzzchar(int m, int h);
void fuzzstr(int m, int h);
void myputs(char *s);
int oct2dec(int i);

int main(int argc, char** argv)
{
     float   f;

     /*
      * Parse command line 
      */
     while (*(++argv) != NULL)
	  if (**argv != SWITCH) {	/* Not a switch, must be a length */
	       if (sscanf(*argv, "%d", &length) != 1)
		    usage();
	       flagn = 1;
	  } else {		/* A switch */
	       switch ((*argv)[1]) {
	       case '0':
		    flag0 = 1;
		    break;
	       case 'a':
		    flaga = 1;
		    break;
	       case 'd':
		    argv++;
		    if (sscanf(*argv, "%f", &f) != 1)
			 usage();
		    flagd = (unsigned) (f * 1000000.0);
		    break;
	       case 'o':
		    flago = 1;
		    argv++;
		    outfile = *argv;
		    break;
	       case 'r':
		    flagr = 1;
		    argv++;
		    infile = *argv;
		    break;
	       case 'l':
		    flagl = 255;
		    if (argv[1] != NULL && argv[1][0] != SWITCH) {
			 argv++;
			 if (sscanf(*argv, "%d", &flagl) != 1 || flagl <= 0)
			      usage();
		    }
		    break;
	       case 'p':
		    flaga = 0;
		    break;
	       case 's':
		    argv++;
		    flags = 1;
		    if (sscanf(*argv, "%d", &seed) != 1)
			 usage();
		    break;
	       case 'm':
		    argv++;
		    flagm = 1;
		    if (sscanf(*argv, "%d", &modulus) != 1)
			 usage();
		    break;
	       case 'e':
		    argv++;
		    flage = 1;
		    if (*argv == NULL)
			 usage();
		    sprintf(epilog, "%s", *argv);
		    break;
	       case 'x':
		    flagx = 1;
		    break;
	       default:
		    usage();
	       }
	  }

     init();
     if (flagr)
	  replay();
     else
	  fuzz();
     myputs(epilog);

     if (flago)
	  if (fclose(out) == EOF) {
	       perror(outfile);
	       exit(1);
	  }
     if (flagr)
	  if (fclose(in) == EOF) {
	       perror(infile);
	       exit(1);
	  }
     return 0;
}


void usage()
{
     puts("Usage: fuzz [-x] [-0] [-a] [-l [strlen]] [-p] [-o outfile]");
     puts("            [-m [modulus] [-r infile] [-d delay] [-s seed]");
     puts("            [-e \"epilog\"] [len]");
     exit(1);
}


/*
 * Initialize random number generator and others 
 */
void init()
{
     long    now;

     /*
      * Init random numbers 
      */
     if (!flags){
	  // if no seed specified, use current time for random seed
          seed = (int)time(&now);
     }

     // if -m is set, restrict the seed value
     if (flagm){
	  seed = seed % modulus;
     }

     srand(seed);

     /*
      * Random line length if necessary 
      */
     if (!flagn)
	  length = rand() % 100000;

     /*
      * Open data files if necessary 
      */
     if (flago)
	  if ((out = fopen(outfile, "wb")) == NULL) {
	       perror(outfile);
	       exit(1);
	  }
     if (flagr) {
	  if ((in = fopen(infile, "rb")) == NULL) {
	       perror(infile);
	       exit(1);
	  }
     } else if (flagx) {
	  printf("%d\n", seed);
	  if (fflush(stdout) == EOF) {
	       perror(progname);
	       exit(1);
          }
	  if (flago) {
	       fprintf(out, "%d\n", seed);
	       if (fflush(out) == EOF) {
		     perror(outfile);
		     exit(1);
               }
	  }
     }
}


/*
 * Replay characters in "in" 
 */
void replay()
{
     int     c;

     while ((c = getc(in)) != EOF)
	  putch(c);
}


/*
 * Decide th effective range of the random characters 
 */
void fuzz()
{
     int     m, h;

     /*
      * Every random character is of the form c = rand() % m + h 
      */
     h = 1;
     m = 255;			/* Defaults, 1-255 */
     if (flag0) {
	  h = 0;
	  m = 256;		/* All ASCII, including 0, 0-255 */
     }
     if (!flaga) {
	  h = 32;
	  m = 95 + (flag0!=0); 	/* Printables, 32-126 */
     }
     if (flagl)
	  fuzzstr(m, h);
     else
	  fuzzchar(m, h);
}


/*
 * Output a character to standard out with delay 
 */
void putch(int i)
{
     char    c;

     c = (char) i;
     if (write(1, &c, 1) != 1) {
	  perror(progname);
	  if (flagr)
	       (void)fclose(in);
	  if (flago)
	       (void)fclose(out);
	  exit(1);
     }
     if (flago)
	  if (write(fileno(out), &c, 1) != 1) {
	       perror(outfile);
	       exit(1);
	  }
     if (flagd)
	  usleep(flagd);
}


/*
 * Make a random character 
 */
void fuzzchar(int m, int h)
{
     int     i,c;

     for (i = 0; i < length; i++) {
	  c = (int) (rand() % m) + h;
	  if (flag0 && !flaga && c == 127)
	       c = 0;
	  putch(c);
     }
}


/*
 * make random strings 
 */
void fuzzstr(int m, int h)
{
     int     i, j, l, c;

     for (i = 0; i < length; i++) {
	  l = rand() % flagl;	/* Line length  */
	  for (j = 0; j < l; j++) {
	       c = (int) (rand() % m) + h;
	       if (flag0 && !flaga && c == 127)
	            c = 0;
	       putch(c);
	  }
	  putch('\n');
     }
}


/*
 * Output the "epilog" with C escape sequences 
 */
void myputs(char *s)
{
     int     c;

     while (strlen(s) != 0) {
	  if (*s == '\\') {
	       switch (*++s) {
	       case 'b':
		    putch('\b');
		    break;
	       case 'f':
		    putch('\f');
		    break;
	       case 'n':
		    putch('\n');
		    break;
	       case 'r':
		    putch('\r');
		    break;
	       case 't':
		    putch('\r');
		    break;
	       case 'v':
		    putch('\v');
		    break;
	       case 'x':
		    s++;
		    (void) sscanf(s, "%2x", &c);
		    putch(c);
		    s++;
		    break;
	       default:
		    if (isdigit(*s)) {
			 (void) sscanf(s, "%3d", &c);
			 putch(oct2dec(c));
			 for (c = 0; c < 3 && isdigit(*s); c++)
			      s++;
			 s--;
		    } else
			 putch(*s);
		    break;
	       }
	  } else
	       putch(*s);
	  s++;
     }
}


/*
 * Octal to Decimal conversion, required by myputs() 
 */
int oct2dec(int i)
{
     char    s[8];
     int     r = 0;

     sprintf(s, "%d", i);
     for (i = 0; i < strlen(s); i++)
	  r = r * 8 + (s[i] - '0');

     return r;
}
