# The Relevance of Classic Fuzz Testing: Have We Solved This One?

### Description

This work is a revisit to Prof. Miller's previous fuzzing works, i.e., [1990](https://dl.acm.org/doi/abs/10.1145/96267.96279), [1995](https://minds.wisconsin.edu/bitstream/handle/1793/59964/TR1268.pdf) and [2006](https://dl.acm.org/doi/abs/10.1145/1145735.1145743). We applied original fuzzing techniques to command-line utilities on multiple platforms and found that 9 crash or hang out of 74 utilities on Linux, 15 out of 78 utilities
on FreeBSD, and 12 out of 76 utilities on MacOS. We found that the failure rates of command-line utilities are higher than those in previous studies. We also provided detailed bug analysis, including when a bug was introduced and when it was solved. Some of the errors that we found have been present in the codebase for many years. Plus, we fuzzed core utilities implemented in Rust.

### Code

In this study, we updated the source code used in the [original fuzzing study](https://dl.acm.org/doi/abs/10.1145/96267.96279). Now it applies to Linux, OS X and FreeBSD.

#### ./src

In this directory:

Makefile

​&emsp;To build fuzz.c and ptyjig.c, run:

​&emsp;```cd ./src && make all```

fuzz.c

​&emsp;A random string generator.

​&emsp;For the usage, run:

​&emsp;```man ./doc/fuzz.man```.

ptyjig.c

​&emsp;A tool to provide input to utilities that read input from the terminal, it is used to test programs such as vim and bash.

​&emsp;For the usage, run:

​&emsp;```man ./doc/ptyjig.man```.

#### ./run_test

In this directory:

./test_Linux/

​&emsp;Name and option pools of each cmd to be tested on Linux.

./test_MacOS/

​&emsp;Name and option pools of each cmd to be tested on MacOS.

./test_FreeBSD/

​&emsp;Name and option pools of each cmd to be tested on FreeBSD.

./end/ 

​&emsp;For each program tested with ptyjig, we specify a string to append to the random input to attempt to terminate the utility. For example, when testing vim, we append the sequence “ESC :q !”. In this way we can distinguish if the program is waiting for more input after the end of random input from a program that is hung.

run.py

​&emsp;Automatic script to test all utilities listed in a configuration file(see ./test_Linux/ or ./test_MacOS/ or ./test_FreeBSD/). 

​&emsp;For the usage, run:

​&emsp;```man ./doc/run.py.1```.

#### ./generate_test

Python scripts to generate random files.

#### ./doc

Man pages for the above files.

### Reference

If you find this implementation useful in your research, please consider citing:

```
@article{miller2020relevance,
  title={The Relevance of Classic Fuzz Testing: Have We Solved This One?},
  author={Miller, Barton and Zhang, Mengxiao and Heymann, Elisa},
  journal={IEEE Transactions on Software Engineering},
  year={2020},
  publisher={IEEE}
}
```