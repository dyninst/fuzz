/*    
 *  Copyright (c) 2020 Lars Fredriksen, Bryan So, Barton Miller
 *
 *  This program is distributed in the hope that it will be useful, but
 *  WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 */

/*
 *  ptyjig -- Super pipe for piping output to Unix utilities.
 *
 *  ptyjig [option(s)] cmd [args]
 *
 *  Run Unix command "cmd" with arguments "args" in background, piping
 *  standard input to "cmd" as its input and prints out "cmd"'s output
 *  to stdout.  This program sets up pseudo-terminal pairs, so that 
 *  it can be used to pipe input to programs that read directly from
 *  tty.
 *
 *  -e suppresses sending of EOF character after stdin exhausted
 *  -s suppresses interrupts.
 *  -x suppresses the standard output.
 *  -i specifies a file to which the standard input is saved.
 *  -o specifies a file to which the standard output is saved.
 *  -d specifies a keystroke delay in seconds (floating point accepted.)
 *  -t specifies a timeout interval.  The program will exit if the
 *     standard input is exhausted and "cmd" does not send output
 *     for "ttt" seconds(takes only integers)
 *  -w specifies another delay parameter. The program starts to send
 *     input to "cmd" after "www" seconds.
 *
 *  Defaults:
 *             -i /dev/nul -o /dev/nul -d 0 -t 2
 *
 *  Examples:
 *         
 *     pty -o out -d 0.2 -t 10 vi text1 < text2
 *
 *        Starts "vi text1" in background, typing the characters in 
 *        "text2" into it with a delay of 0.2 sec between each char-
 *        acter, and save the output by "vi" to "out".  The program
 *        ends when "vi" stops outputting for 10 seconds.
 *
 *     pty -i in -o out csh
 *
 *        Behaves like "script out" except the keystrokes typed by
 *        a user are also saved into "in".
 *
 *  Authors:
 *
 *    Bryan So, Lars Fredriksen, Barton P. Miller
 *
 *  Updated by:
 *
 *    Mengxiao Zhang, Emma He (April 2020)
 *
 */

// For more debug info, define DEBUG, or define DEBUG_off to suppress it.
#define DEBUG_off

#include <sys/time.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/file.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <signal.h>
#include <stdio.h>
#include <strings.h>
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>

int posix_openpt(int flags);
int grantpt(int fd);
int unlockpt(int fd);
char *ptsname(int fd);
int ptsname_r(int fd, char *buf, size_t buflen);


/* GLOBAL VARIABLES */
#define CHILD 0
#define TRUE  1
#define FALSE 0

char     flage = TRUE;
int      flags = FALSE;
int      flagx = FALSE;
int      flagi = FALSE;
int      flago = FALSE;
// Timeout interval in seconds
unsigned flagt = 2;   
// Starting wait in useconds
unsigned flagw = FALSE;         
// Delay between keystrokes in useconds
unsigned flagd = FALSE;         

char* namei;
char* nameo;
FILE* filei;
FILE* fileo;

// pids for the reader, writer and exec
int readerPID = -1;
int writerPID = -1;
int execPID   = -1; 

// tty and pty file descriptors
int   tty = -1;
int   pty = -1; 

char  ttyNameUsed[40];
char* progname;

// return value of functions
int ret;

// for more verbose output at the end of execution
// makes reason for dying more obvious
struct  mesg {
  char    *iname;
  char    *pname;
} mesg[] = {
  {0,      0},
  {"HUP",  "Hangup"},
  {"INT",  "Interrupt"},
  {"QUIT", "Quit"},
  {"ILL",  "Illegal instruction"},
  {"TRAP", "Trace/BPT trap"},
  {"IOT",  "IOT trap"},
  {"EMT",  "EMT trap"},
  {"FPE",  "Floating exception"},
  {"KILL", "Killed"},
  {"BUS",  "Bus error"},
  {"SEGV", "Segmentation fault"},
  {"SYS",  "Bad system call"},
  {"PIPE", "Broken pipe"},
  {"ALRM", "Alarm clock"},
  {"TERM", "Terminated"},
  {"URG",  "Urgent I/O condition"},
  {"STOP", "Stopped (signal)"},
  {"TSTP", "Stopped"},
  {"CONT", "Continued"},
  {"CHLD", "Child exited"},
  {"TTIN", "Stopped (tty input)"},
  {"TTOU", "Stopped (tty output)"},
  {"IO",   "I/O possible"},
  {"XCPU", "Cputime limit exceeded"},
  {"XFSZ", "Filesize limit exceeded"},
  {"VTALRM","Virtual timer expired"},
  {"PROF", "Profiling timer expired"},
  {"WINCH","Window size changed"},
  {0,      "Signal 29"},
  {"USR1", "User defined signal 1"},
  {"USR2", "User defined signal 2"},
  {0,      "Signal 32"}
};


// A flag indicating status of the writer
int writing = TRUE;

// A flag indicating status of the executing program
int executing = TRUE;

// Unfix the above and exit when we are done. 
void done() {
#ifdef DEBUG
  printf("ptyjig: in done()\n");
#endif

  // Close output files if opened
  if(flagi) {
    fclose(filei);
    flagi = FALSE;
  }

  if(flago) {
    fclose(fileo);
    flago = FALSE;
  }

}

// Signal handler for SIGCHLD
void sigchld(int sig) {
  int pid;
  //union wait status;
  int status;

#ifdef DEBUG
  printf("ptyjig: got signal SIGCHLD\n");
#endif

  // Guarantee to return since a child is dead
  pid = wait3((int*)&status, WUNTRACED, 0);  
#ifdef DEBUG
    printf("sigchld wait3: pid = %d\n",pid);
#endif

  if(pid) {
#ifdef DEBUG
    printf("ptyjig: pid = %d\n",pid);
    printf("ptyjig: status = %d %d %d %d %d\n",
            WTERMSIG(status),WCOREDUMP(status),WEXITSTATUS(status),
            WIFSTOPPED(status),WSTOPSIG(status));

#endif

    if(WSTOPSIG(status) == SIGTSTP) {
      kill(pid, SIGCONT);
    }
    else {
      signal(SIGINT,   SIG_DFL);
      signal(SIGQUIT,  SIG_DFL); 
      signal(SIGTERM,  SIG_DFL); 
      signal(SIGWINCH, SIG_DFL); 
      signal(SIGCHLD,  SIG_IGN);

      done();

      if(pid != execPID) {
#ifdef DEBUG
        printf("ptyjig: somebody killed my child\n");
        printf("ptyjig: killing execPID = %d\n", execPID);
#endif
        // kill the exec too
        kill(-execPID, SIGKILL);          
        // use the same method to suicide
        kill(readerPID, WTERMSIG(status)); 
      }

      // Just to make sure it is killed
      kill(-execPID, SIGKILL); 

      if(pid != writerPID && writerPID != -1) {
#ifdef DEBUG
        printf("ptyjig: killing writerPID = %d\n", writerPID);
#endif
        kill(writerPID, SIGKILL);
      }

      if(WTERMSIG(status)) {
        printf("ptyjig: %s: %s%s\n",progname,
               mesg[WTERMSIG(status)].pname,
               WCOREDUMP(status) ? " (core dumped)" : "");
      }

      // If process terminates normally, return its retcode
      // If abnormally, return termsig.  This is not exactly
      // the same as csh, since the csh method is not too obvious

      exit(WTERMSIG(status) ? WTERMSIG(status) : WEXITSTATUS(status));
    }

    exit(0);
  }
}

// Clean up processes
void clean() {
#ifdef DEBUG
  printf("ptyjig: in clean()\n");
#endif

  // Not necessary for sigchld to take over
  signal(SIGCHLD, SIG_IGN); 

  // must close files, and kill all running processes
  if(execPID != -1) {
#ifdef DEBUG
    printf("ptyjig: killing execPID = %d\n", execPID);
#endif
    kill(-execPID, SIGKILL);
  }

  if(writerPID != -1) {
#ifdef DEBUG
    printf("ptyjig: killing writerPID = %d\n", writerPID);
#endif
    kill(writerPID, SIGKILL);
  }

  done();
}

// Handle window size change SIGWINCH
void sigwinch(int sig) {
  struct winsize ws;

  ret = ioctl(0,   TIOCGWINSZ, &ws);
  if (ret < 0) {
    fprintf(stderr, "Error %d on ioctl(0, TIOCGWINSZ, &ws)\n", errno);
    exit(1);
  }
  ret = ioctl(pty, TIOCSWINSZ, &ws);
  if (ret < 0) {
    fprintf(stderr, "Error %d on ioctl(pty, TIOCGWINSZ, &ws)\n", errno);
    exit(1);
  }

  kill(-execPID, SIGWINCH);
}

// Handle user interrupt SIGINT
void clean_int(int sig) {
#ifdef DEBUG
  printf("ptyjig: got signal SIGINT\n");
#endif

  signal(SIGINT, SIG_DFL);
  clean();

  kill(readerPID, SIGINT);
}

// Handle quit signal SIGQUIT
void clean_quit(int sig) {
#ifdef DEBUG
  printf("ptyjig: got signal SIGQUIT\n");
#endif

  clean();
  signal(SIGQUIT, SIG_DFL);
  kill(readerPID, SIGQUIT);
}
 
// Handle user terminate signal SIGTERM
void clean_term(int sig) {
#ifdef DEBUG
  printf("ptyjig: got signal SIGTERM\n");
#endif

  clean();
  signal(SIGTERM, SIG_DFL);

  kill(readerPID, SIGTERM);
}

// Opens a master pseudo-tty device
void setup_pty() {
  printf("enter setup_pty\n");
  int rc;

  pty = posix_openpt(O_RDWR);
  if (pty < 0) {
    fprintf(stderr, "Error %d on posix_openpt()\n", errno);
    exit(1);
  }

  rc = grantpt(pty);
  if (rc != 0) {
    fprintf(stderr, "Error %d on grantpt()\n", errno);
    exit(1);
  }

  rc = unlockpt(pty);
  if (rc != 0) {
    fprintf(stderr, "Error %d on unlockpt()\n", errno);
    exit(1);
  }
}

// Opens the slave device. 
void setup_tty() {
  char* name_of_slave = ptsname(pty);
  if(name_of_slave == NULL) {
    perror("fail to open slave device\n");
    exit(1);
  }
  tty = open(name_of_slave, O_RDWR);
  if(tty < 0) {
    perror(ttyNameUsed);
    exit(1);
  }
}

// Sets boolean to false to stop CMD's execution
void execute_done(int sig) {
  executing = FALSE;
}

// Fork off a copy and execute "arg".  Before executing, assign "tty" to
// stdin, stdout and stderr, so that the output of the child program can be
// recorded by the other end of "tty". 
void execute(char** cmd) {
  int fstdin, fstdout, fstderr;

  signal(SIGUSR1, execute_done);

  if((execPID = fork()) == -1) {
    fprintf(stderr, "Error %d on execPID = fork()\n", errno);
    exit(1);
  }

  if(execPID == CHILD) {
    // save copies in case exec fails
    fstdin  = dup(0);
    if(fstdin < 0) {
      fprintf(stderr, "Error %d on fstdin = dup(0)\n", errno);
      exit(1);
    }
    fstdout = dup(1);
    if(fstdout < 0) {
      fprintf(stderr, "Error %d on fstdout = dup(1)\n", errno);
      exit(1);
    }
    fstderr = dup(2); 
    if(fstderr < 0) {
      fprintf(stderr, "Error %d on fstderr = dup(2)\n", errno);
      exit(1);
    }

    ret = setsid();
    if(ret < 0) {
      fprintf(stderr, "Error %d on ret = setsid()\n", errno);
      exit(1);
    }

    setup_tty();
    // copy tty to stdin  
    ret = dup2(tty, 0);        
    if(ret < 0) {
      fprintf(stderr, "Error %d on ret = dup2(tty, 0)\n", errno);
      exit(1);
    }
    // copy tty to stdout  
    ret = dup2(tty, 1);        
    if(ret < 0) {
      fprintf(stderr, "Error %d on ret = dup2(tty, 1)\n", errno);
      exit(1);
    }
    // copy tty to stderr  
    ret = dup2(tty, 2);        
    if(ret < 0) {
      fprintf(stderr, "Error %d on ret = dup2(tty, 2)\n", errno);
      exit(1);
    }

    if(tty > 2) {
      close(tty);
    }

    // suppress signals if -s present 
    if(flags) {        
      signal(SIGINT,  SIG_IGN);
      signal(SIGQUIT, SIG_IGN);
      signal(SIGTSTP, SIG_IGN);
    }

    // Better be setup to handle a SIGUSR1 
    kill(getppid(), SIGUSR1);

    execvp(cmd[0], cmd);

    // IF IT EVER GETS HERE, error when executing "cmd"  
    ret = dup2(fstdin,  0);
    if(ret < 0) {
      fprintf(stderr, "Error %d on dup2(fstdin, 0)\n", errno);
      exit(1);
    }
    ret = dup2(fstdout, 1);
    if(ret < 0) {
      fprintf(stderr, "Error %d on dup2(fstdout, 1)\n", errno);
      exit(1);
    }
    ret = dup2(fstderr, 2);
    if(ret < 0) {
      fprintf(stderr, "Error %d on dup2(fstderr, 2)\n", errno);
      exit(1);
    }

    perror(cmd[0]);

    exit(1);
  }
#ifdef DEBUG
    printf("execPID: pid = %d\n",execPID);
#endif

  // let child run until it gives signal 
  while(executing); 

  usleep(flagw);

#ifdef DEBUG
  printf("ptyjig: execPID = %d\n", execPID);
#endif
}

// Sleeps for 1 second, then KILLs PID execPID using SIGKILL
void reader_done(int sig) {
  // Let execPID die naturally
  sleep(1);   

#ifdef DEBUG
  printf("ptyjig: killing execPID = %d\n", execPID);
#endif

  // If it doesn't die on its own, kill it 
  kill(-execPID, SIGKILL); 
}

// Sets boolean to false to stop writer
void writer_done(int sig) {
  writing = FALSE;
  alarm(flagt);
}

// Read from stdin and send everything character read to "pty".  Record the
// keystrokes in "filei" if -i flag is on. 
void writer() {
  char c;

  // Read from keyboard continuously and send it to "pty" 
  while(read(0, &c, 1) == 1) { 
    if(write(pty, &c, 1) != 1) {
      break;
    }

    if (flagi) {
      // Do not send '\r', send '\n' instead 
      if(c == '\r') {
        c = '\n';
      }

      if(write(fileno(filei), &c, 1) != 1) {
        perror(namei);
        break;
      }
    }

    // Delay writing to "pty" if flagged 
    if(flagd) {
      usleep(flagd);
    }
  }

  if(flage) {
    (void)write(pty, &flage, 1);
  }

#ifdef DEBUG
  printf("ptyjig: writer finished\n");
#endif

  // tell reader to quit if no more char from exec
  kill(readerPID, SIGUSR1); 

  // XXX: INFINITE LOOP: Wait until parent kills me
  while(1);  
}

// Read from "pty" and send it to stdout 
void reader() {
  char    c[BUFSIZ];
  int     i;

#ifdef DEBUG
    printf("reader(): pid = %d\n",getpid());
#endif

  // Continuously read from "pty" until exhausted.  Write every character
  // to stdout if -x flag is not present, and to "fileo" if -o flag is on.   
  signal(SIGALRM, reader_done);
  signal(SIGUSR1, writer_done);

  while ((i = read(pty, c, sizeof(c))) > 0) {
    if(!flagx) {
      if(write(1, c, i) != i) {
        exit(1);
      }
    }

    if(flago) {
      if(write(fileno(fileo), c, i) != i) {
        perror(nameo);
        exit(1);
      }
    }

    // The following "if" essentially means when "writer" is done, and
    // there is no more keystroke coming from "pty" wait for "flagt"
    // seconds and quit.  If during this wait, a character comes from
    // "pty", then the wait is set back. 
    if(!writing) {
      alarm(flagt);
    }
  }

#ifdef DEBUG
  printf("ptyjig: reader finished\n");
#endif

  reader_done(0);
}

void doreader() {
  reader();
}

// Fork writer 
void dowriter() {
  if((writerPID = fork()) == -1) {
    fprintf(stderr, "Error %d on writerPID = fork()\n", errno);
    exit(1);
  } 

  if(writerPID == CHILD) {
    writerPID = getpid();
    writer();
  }
#ifdef DEBUG
    printf("dowriter(): pid = %d\n",writerPID);
#endif
}

// Display help screen 
void usage() {
  printf("  ptyjig -- Super pipe for piping output to Unix utilities.\n\n");
  printf("  Usage:\n");
  printf("    ptyjig [options] cmd <args>\n\n");
  printf("  Description:\n");
  printf("    Run command \"cmd\" with arguments \"args\" in background, piping\n");
  printf("    stdin to \"cmd\" as its input and prints out \"cmd\"'s output\n");
  printf("    to stdout.  This program sets up pseudo-terminal pairs, so that\n");
  printf("    it can be used to pipe input to programs that read directly from\n");
  printf("    a tty interface.\n\n");
  printf("  Options:\n");
  printf("    -e          suppresses sending EOF char after stdin exhausted\n");
  printf("    -s          suppresses interrupts\n");
  printf("    -x          suppresses the standard output\n");
  printf("    -i FILEIN   standard input saved to file FILEIN\n");
  printf("    -o FILEOUT  standard output saved to file FILEOUT\n");
  printf("    -d DELAY    use a keystroke delay of DELAY seconds (accepts floating pt)\n");
  printf("    -t TIMEOUT  kill \"cmd\" if stdin exhausted and \"cmd\" doesn't send\n");
  printf("                output for TIMEOUT seconds (takes only integer)\n");
  printf("    -w WAIT     wait WAIT seconds before streaming input to \"cmd\"\n\n");
  printf("  Defaults:\n");
  printf("    -i /dev/null -o /dev/null -d 0 -t 2\n\n");
  printf("  Examples:\n\n");
  printf("     ptyjig -o out -d 0.05 -t 10 vi text1 < text2\n\n");
  printf("       Starts \"vi text1\" in background, typing the characters\n");
  printf("       in \"text2\" into it with a delay of 0.05 sec between each\n");
  printf("       character, and save the output of \"vi\" to \"out\".\n");
  printf("       Program ends when \"vi\" stops outputting for 10 seconds.\n\n");
  printf("     ptyjig -i in -o out csh\n\n");
  printf("       Behaves like \"script out\" except the keystrokes typed by\n");
  printf("       a user are also saved into \"in\".\n");
  printf("  Authors: \n");
  printf("     Lars Fredriksen, Bryan So, Barton Miller\n\n");
  printf("  Updated by: \n");
  printf("     Gregory Smethells, Brian Bowers, Karlen Lie\n");

  exit(1);
}

// Parse the args, start reader and writer, fork the process to be "piped" to 
int main(int argc, char** argv) {
  int     num;
  int     cont;
  float   f;
  unsigned int t;
  extern int   optind;
  extern char* optarg;

  struct termios termIOSettings;

#ifdef DEBUG
    printf("main: pid = %d\n",getpid());
#endif


  // Parse the arguments to ptyjig. A ":" after a letter means
  // that flag takes an argument value and isn't just a boolean
  while((argc > 1) && (argv[1][0] == '-')) {
    num  = 1;
    cont = TRUE;

    while(cont) {
      switch(argv[1][num]) {
        case 'e':
          flage = FALSE;
          break;

        case 's':
          flags = TRUE;
          break;

        case 'x':
          flagx = TRUE;
          break;

        case 'i':
          flagi = TRUE;
          namei = argv[2];
          argc--;
          argv++;
          cont = FALSE;
          break;

        case 'o':
          flago = TRUE;
          nameo = argv[2];
          argc--;
          argv++;
          cont = FALSE;
          break;

        case 'd':
          if(sscanf(argv[2], "%f", &f) < 1) {
            usage();
          }
  
          argc--;
          argv++;
          cont = FALSE;
  
          // Convert to microseconds 
          flagd = (unsigned)(f * 1000000.0);
          break;

        case 't':
          if(sscanf(argv[2], "%u", &t) < 1) {
            usage();
          }

          argc--;
          argv++;
          cont = FALSE;

          // Convert to microseconds 
          flagt = t;
          break;

        case 'w':
          if(sscanf(argv[2], "%f", &f) < 1) {
            usage();
          }
 
          argc--;
          argv++;
          cont = FALSE;

          // Convert to microseconds 
          flagw = (unsigned)(f * 1000000.0);
          break;

        default:
          usage();
      }
 
      num++;
    
      if(cont && !argv[1][num]) {
        cont = FALSE;
      }
    }

    argc--;
    argv++;
  }


  // Now, argv point to a command 
  if(!argv[1]) {
    usage();
  }

  // Possibly open a "save the input file" 
  if(flagi) {
    filei = fopen(namei, "wb");

    if(filei == NULL) {
      perror(namei);
      exit(1);
    }
  }

  // Possible open a "save the output file"
  if(flago) {
    fileo = fopen(nameo, "wb");

    if(fileo == NULL) {
      perror(nameo);
      exit(1);
    }
  }


  // open an arbitrary pseudo-terminal pair 
  setup_pty();

  // Get Attributes for Master
  tcgetattr(pty, &termIOSettings);

  // Make output as RAW as possible
  cfmakeraw(&termIOSettings);

  termIOSettings.c_lflag |= ECHO;

  // Set Attributes for Master to RAWed version of "termIOSettings"
  (void) tcsetattr(pty, TCSANOW, &termIOSettings);

  // fork and execute test program with arguments 
  progname = argv[1]; 
  execute((char **) &argv[1]);



  signal(SIGWINCH, sigwinch); 

  readerPID = getpid(); 

  dowriter();

  // put here instead of above to avoid invoking clean_XYZ twice 
  signal(SIGQUIT, clean_quit); 
  signal(SIGTERM, clean_term); 
  signal(SIGINT,  clean_int); 

  doreader();


  // process the return value of cmd
  int pid, status;

#ifdef DEBUG
  printf("ptyjig: got signal SIGCHLD\n");
#endif

  // Guarantee to return since a child is dead 
  pid = wait3((int*)&status, WUNTRACED, 0);  
#ifdef DEBUG
    printf("sigchld wait3: pid = %d\n",pid);
#endif

  if(pid) {
#ifdef DEBUG
    printf("ptyjig: pid = %d\n",pid);
    printf("ptyjig: status = %d %d %d %d %d\n",
            WTERMSIG(status),WCOREDUMP(status),WEXITSTATUS(status),
            WIFSTOPPED(status),WSTOPSIG(status));

#endif
    int ret = 0;
    if(WSTOPSIG(status) == SIGTSTP) {
      kill(pid, SIGCONT);
    }
    else {
      signal(SIGINT,   SIG_DFL);
      signal(SIGQUIT,  SIG_DFL); 
      signal(SIGTERM,  SIG_DFL); 
      signal(SIGWINCH, SIG_DFL); 
      signal(SIGCHLD,  SIG_IGN);

      done();

      if(pid != execPID) {
#ifdef DEBUG
        printf("ptyjig: somebody killed my child\n");
        printf("ptyjig: killing execPID = %d\n", execPID);
#endif
        // kill the exec too 
        kill(-execPID, SIGKILL);          
        // use the same method to suicide 
        kill(readerPID, WTERMSIG(status)); 
      }

      // Just to make sure it is killed 
      kill(-execPID, SIGKILL); 

      if(pid != writerPID && writerPID != -1) {
#ifdef DEBUG
        printf("ptyjig: killing writerPID = %d\n", writerPID);
#endif
        kill(writerPID, SIGKILL);
      }

      if(WTERMSIG(status)) {
        printf("ptyjig: %s: %s%s\n",progname,
               mesg[WTERMSIG(status)].pname,
               WCOREDUMP(status) ? " (core dumped)" : "");
        ret = 128 + WTERMSIG(status);
      }
    }
    return ret;
  }
}


