#  Copyright (c) 2020 Emma He, Mengxiao Zhang, Barton Miller
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

# this script is used to generate big test cases.

import os
import subprocess
import sys
import random
import getopt
import re
import datetime

# define variables

# return_value is the lowest return value with special meaning
return_value = 126
float_rand = 0.5
arg_num = 6

# redirect the output to /dev/null, otherwise the shell will be overwhelmed by outputs
fnull = open(os.devnull, 'w')
ptyjig_path = "../src/ptyjig"

first_file_for_more = "/p/paradyn/papers/fuzz2020/testcases/Large3/t150"

usage = "Usage: python3 run.py configuration_file [-i inputfile] [-p prefix] [-t timeout] [-o outputfile]"

# return a random subset of s, each element has 0.5 probability
def random_subset(s):
  out = ""
  for el in s:
    # random coin flip
    if random.random() > float_rand:
      out = out + el + " "
  return out

def line_commented(line):
  return line.startswith("//")


def line_syntax_valid(line):
  if(not line.startswith("//") \
    and not line.startswith("file ") \
    and not line.startswith("stdin ") \
    and not line.startswith("cp ") \
    and not line.startswith("two_files ") \
    and not line.startswith("pty ")
    ):
    return False

  # if specify option pool, there should be a pair of []
  if(line.count("[") > 0 or line.count("]") > 0):
    if(line.count("[") != 1 or line.count("]") != 1):
      return False
    # if [ is on the right of ]
    elif(line.find("[") > line.find("]")):
      return False
  
  return True

def get_options_from_pool(option_part_of_line):
  # keep characters on the left of [ and characters on the right of ]
  idx_left = option_part_of_line.find("[")
  idx_right = option_part_of_line.find("]")
  if(idx_left >= 0):
    return option_part_of_line[idx_left+1: idx_right]
  else:
    return ""

# leave a space for randomly selected options
def get_other_options(option_part_of_line):
  # return string on the left of [ and string on the right of ]
  idx_left = option_part_of_line.find("[")
  idx_right = option_part_of_line.find("]")
  if(idx_left >= 0):
    return option_part_of_line[0: idx_left] + " %s " + option_part_of_line[idx_right+1: ]
  else:
    return option_part_of_line + " %s"

def parse_a_line(line):

  # filter out redundant white space
  line = " ".join(line.split())

  # type is "stdin", "file", "two_files", "cp" or "pty"
  test_type = line.split()[0]

  # get the name of temporary file if a utility needs to copy test case to it
  # if cp, file name is specified, e.g., t.c
  if(test_type == "cp"):
    new_file_name = line.split()[1]
  # if pty, just copy test cases as tmp
  elif(test_type == "pty"):
    new_file_name = "tmp"
  # other test_types don't need to copy test cases
  else:
    new_file_name = ""

  # get the name of utilities
  # if cp, utility name is the third element of line.split(), e.g., cc from "cp t.c cc"
  if(test_type == "cp"):
    utility_name = line.split()[2]
  # otherwise, utility name is the second element of line.split(), e.g., flex from "stdin flex"
  else:
    utility_name = line.split()[1]

  # option_part_of_line is the part behind utility name
  if(test_type == "cp"):
    option_part_of_line = (line+" ").split(" ", 3)[3]
  else:
    option_part_of_line = (line+" ").split(" ", 2)[2]

  # get the options in option pool
  all_options_from_pool = get_options_from_pool(option_part_of_line)
  other_options = get_other_options(option_part_of_line)


  if(test_type == "stdin"):
    # leave a space for testcase
    cmd = utility_name \
              + " " + other_options \
              + " < " + "%s" 

  elif(test_type == "file"):
    # leave a space for testcase
    cmd = utility_name \
              + " " + other_options \
              + " " + "%s"

  elif(test_type == "cp"):
    cmd = utility_name \
              + " " + other_options \
              + " " + new_file_name

  elif(test_type == "two_files"):
    # leave two space for testcases
    cmd = utility_name \
              + " " + other_options \
              + " " + "%s" \
              + " " + "%s"

  elif(test_type == "pty"):
    # -d delay will be set in run_pty

    # more and less are special, it requires two files. The first file is the file to operate on, the second file provides random control sequence. Before the testing, copy one big test case to /tmp/tmp as the first file.
    if(utility_name == "more" or utility_name == "less"):
        cmd = ptyjig_path \
              + " " + "-d" + " " + "%g" \
              + " " + "-x" \
              + " " + utility_name \
              + " " + other_options \
              + " " + "/tmp/tmp" \
              + " < " + new_file_name
    else:
        cmd = ptyjig_path \
              + " " + "-d" + " " + "%g" \
              + " " + "-x" \
              + " " + utility_name \
              + " " + other_options \
              + " < " + new_file_name


  log_name = "%s.%s" % (os.path.basename(utility_name), test_type)

  return cmd, test_type, utility_name, new_file_name, all_options_from_pool, log_name

# run "file"
def run_file(cmd, utility_name, log_path, all_options_from_pool, testcase_list): 

  # if the log exists and have been finished, go to test the next utility
  if os.path.exists(log_path) and os.stat(log_path).st_size != 0:
    with open(log_path, "r") as f:
      if f.readlines()[-1] == "finished\n":
        return

  # otherwise, create the log or overwrite it 
  log_writer = open(log_path, "w")
  log_writer.write("start: %s\n" % line)

  for testcase in testcase_list:

    options_sampled_from_pool = random_subset(all_options_from_pool.split())
    final_cmd = cmd % (options_sampled_from_pool, testcase)
    print("running: %s" % final_cmd)

    try:
      retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)

    except(subprocess.TimeoutExpired):
      log_writer.write("%s hung\n" % final_cmd)

    else:
      print("retcode is %d" % retcode)
      if(retcode == 127):
        log_writer.write("%s not found\n" % utility_name)
        break
      # check return value, record exit code with special meaning
      if retcode >= return_value or retcode < 0:
        log_writer.write("%s failed, error: %d\n" % (final_cmd, retcode))

  log_writer.write("%s\n" % datetime.datetime.now())
  log_writer.write("finished\n")
  log_writer.close()
  print("finished: %s" % line)

# run "stdin", so far it's identical to run_file
def run_stdin(cmd, utility_name, log_path, all_options_from_pool, testcase_list): 

  # if the log exists and have been finished, go to test the next utility
  if os.path.exists(log_path) and os.stat(log_path).st_size != 0:
    with open(log_path, "r") as f:
      if f.readlines()[-1] == "finished\n":
        return

  # otherwise, create the log or overwrite it 
  log_writer = open(log_path, "w")
  log_writer.write("start: %s\n" % line)

  for testcase in testcase_list:

    options_sampled_from_pool = random_subset(all_options_from_pool.split())
    final_cmd = cmd % (options_sampled_from_pool, testcase)
    print("running: %s" % final_cmd)

    try:
      retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)

    except(subprocess.TimeoutExpired):
      log_writer.write("%s hung\n" % final_cmd)

    else:
      print("retcode is %d" % retcode)
      if(utility_name not in ("sh", "csh", "zsh") and retcode == 127):
        log_writer.write("%s not found\n" % utility_name)
        break
      # check return value, record exit code with special meaning
      if retcode >= return_value or retcode < 0:
        log_writer.write("%s failed, error: %d\n" % (final_cmd, retcode))

  log_writer.write("%s\n" % datetime.datetime.now())
  log_writer.write("finished\n")
  log_writer.close()
  print("finished: %s" % line)

# run "cp", need to copy test case firstly
def run_cp(cmd, utility_name, new_file_name, log_path, all_options_from_pool, testcase_list): 

  # if the log exists and have been finished, go to test the next utility
  if os.path.exists(log_path) and os.stat(log_path).st_size != 0:
    with open(log_path, "r") as f:
      if f.readlines()[-1] == "finished\n":
        return

  # otherwise, create the log or overwrite it 
  log_writer = open(log_path, "w")
  log_writer.write("start: %s\n" % line)

  for testcase in testcase_list:

    options_sampled_from_pool = random_subset(all_options_from_pool.split())
    final_cmd = cmd % options_sampled_from_pool

    # copy test case to a new temporary file with a specified name
    subprocess.call(["cp %s %s" % (testcase, new_file_name)], shell=True)

    print("running: %s" % final_cmd)

    try:
      retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)

    except(subprocess.TimeoutExpired):
      log_writer.write("%s hung, testcase is %s\n" % (final_cmd, testcase))

    else:
      print("retcode is %d" % retcode)
      if(retcode == 127):
        log_writer.write("%s not found\n" % utility_name)
        break
      # check return value, record exit code with special meaning
      if retcode >= return_value or retcode < 0:
        log_writer.write("%s failed, error: %d\n" % (final_cmd, retcode))

    finally:
      subprocess.call("rm %s" % new_file_name, shell=True)

  log_writer.write("%s\n" % datetime.datetime.now())
  log_writer.write("finished\n")
  log_writer.close()
  print("finished: %s" % line)


# run "two_files", so far it's identical to run_file
def run_two_files(cmd, utility_name, log_path, all_options_from_pool, testcase_list): 

  # if the log exists and have been finished, go to test the next utility
  if os.path.exists(log_path) and os.stat(log_path).st_size != 0:
    with open(log_path, "r") as f:
      if f.readlines()[-1] == "finished\n":
        return

  # otherwise, create the log or overwrite it 
  log_writer = open(log_path, "w")
  log_writer.write("start: %s\n" % line)

  for testcase in testcase_list:

    options_sampled_from_pool = random_subset(all_options_from_pool.split())

    # randomly select two testcases each time
    testcase1 = random.choice(testcase_list)
    testcase2 = random.choice(testcase_list)
    final_cmd = cmd % (options_sampled_from_pool, testcase1, testcase2)
    print("running: %s" % final_cmd)

    try:
      retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)

    except(subprocess.TimeoutExpired):
      log_writer.write("%s hung\n" % final_cmd)

    else:
      print("retcode is %d" % retcode)
      if(retcode == 127):
        log_writer.write("%s not found\n" % utility_name)
        break
      # check return value, record exit code with special meaning
      if retcode >= return_value or retcode < 0:
        log_writer.write("%s failed, error: %d\n" % (final_cmd, retcode))

  log_writer.write("%s\n" % datetime.datetime.now())
  log_writer.write("finished\n")
  log_writer.close()
  print("finished: %s" % line)


# run "pty"
def run_pty(cmd, utility_name, log_path, all_options_from_pool, testcase_list):  

  # if the log exists and have been finished, go to test the next utility
  if os.path.exists(log_path) and os.stat(log_path).st_size != 0:
    with open(log_path, "r") as f:
      if f.readlines()[-1] == "finished\n":
        return

  # otherwise, create the log or overwrite it 
  log_writer = open(log_path, "w")
  log_writer.write("start: %s\n" % line)

  for testcase in testcase_list:

    options_sampled_from_pool = random_subset(all_options_from_pool.split())

    # copy test case to tmp and append the designed end file 
    subprocess.call("cat %s ./end/end_%s > tmp" % (testcase, utility_name), shell=True, stdout=fnull, stderr=subprocess.STDOUT)

    fr = open("tmp", "rb")
    s = fr.read()
    fr.close()
    # remove all ^z in tmp
    s = s.replace(b"\x1a", b"")
    # remove all ^c in tmp
    s = s.replace(b"\x03", b"")
    # remove all ^\ in tmp
    s = s.replace(b"\x1c", b"")
    # remove all \x9a in tmp
    s = s.replace(b"\x9a", b"")
    # remove all \xc0 in tmp
    s = s.replace(b"\xc0", b"")

    # Z or z will suspend telnet 
    if(utility_name == "telnet"):
        s = s.replace(b"Z", b"")
        s = s.replace(b"z", b"")
    # command F will make less show the file updates in real time, it requires an interrupt to quit.
    if(utility_name == "less"):
        s = s.replace(b"F", b"")
    fw = open("tmp", "wb")
    fw.write(s)
    fw.close()

    # htop and top need to be fed input slowly, otherwise it can't quit
    if(utility_name == "htop"):
      final_cmd = cmd % (0.01, options_sampled_from_pool)
    elif(utility_name == "top"):
      final_cmd = cmd % (0.01, options_sampled_from_pool)
    else:
      final_cmd = cmd % (0.001, options_sampled_from_pool)

    # more needs two files, one file provides random control sequence, another file is the file to read
    if(utility_name == "more" or utility_name == "less"):
      subprocess.call(["cp %s /tmp/tmp" % first_file_for_more], shell=True)
    

    # print final_cmd to stdin
    print("running: %s, test case: %s" % (final_cmd, testcase))

    # debug
    f = open("log", "w")
    f.write("running: %s, current test case: %s" % (final_cmd, testcase))
    f.close()
    # debug

    try:
      retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)

    except(subprocess.TimeoutExpired):
      log_writer.write("%s hung, testcase is %s\n" % (final_cmd, testcase))

    else:
      print("retcode is %d" % retcode)
      if(retcode == 127):
        log_writer.write("%s not found\n" % utility_name)
        break

      # killed by built-in timer of ptyjig because of timeout
      if(retcode == 137 or retcode == -9):
        log_writer.write("%s hung, testcase is %s\n" % (final_cmd, testcase))
      # check return value, record exit code with special meaning
      elif retcode >= return_value or retcode < 0:
        log_writer.write("%s failed, testcase is %s, error: %d\n" % (final_cmd, testcase, retcode))

    finally:
      subprocess.call("rm tmp", shell=True)

  log_writer.write("%s\n" % datetime.datetime.now())
  log_writer.write("finished\n")
  log_writer.close()
  print("finished: %s" % line)




# the script start here
if __name__ == "__main__":

  # options

  # where are the test cases
  test_dir = "../../testcases"

  # the result will be saved in output_dir, each cmd corresponds to a result file 
  result_dir = "./result"

  # the script will test all the files starting with a specified prefix. Prefix is empty string by default, 
  # which means all the files in test_dir will be tested.
  prefix = ""

  # if the cmd does not finish in timeout(300 by default) seconds, the test result will be considered as a hang
  timeout = 300

  # too few arguments
  if(len(sys.argv) < 2):
    print("too few arguments")
    print(usage)
    sys.exit(1)
  # -h or --help
  elif(len(sys.argv) == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help")):
    print(usage)
    sys.exit(1)

  # get configuration_file and check if it exists
  configuration_file = sys.argv[1]
  if(not os.path.isfile(configuration_file)):
    print("configuration_file does not exist")
    print(usage)
    sys.exit(1)

  try:
    opts, args = getopt.getopt(sys.argv[2:],"i:o:p:t:",["ifile=", "ofile=", "prefix=", "timeout="])
  except getopt.GetoptError as err:
    print("error on arguments")
    print(usage)
    sys.exit(1)

  for opt, arg in opts:
    if(opt in ("-i", "--ifile")):
      test_dir = arg
    elif(opt in ("-o", "--ofile")):
      result_dir = arg
    elif(opt in ("-p", "--prefix")):
      prefix = arg
    elif(opt in ("-t", "--timeout")):
      timeout = int(arg)

  if not os.path.isdir(test_dir):
    print("%s is not a directory" % test_dir)
    print(usage)
    sys.exit(1)

  if result_dir == "":
    print("please provide valid directory for result")
    print(usage)
    sys.exit(1)


  # print out the parameters
  print("Input directory is %s" % test_dir)
  print("Output directory is %s" % result_dir)
  print("Configuration file is %s" % configuration_file)
  print("Prefix is %s" % "None" if(prefix == "") else prefix)
  print("Timeout is %d" % timeout)

  # make directory to save output
  if not os.path.exists(result_dir):
    os.makedirs(result_dir)

  # get path of all test cases
  testcase_list = []
  testcase_list = os.listdir(test_dir)
  testcase_list = [file for file in testcase_list if file.startswith(prefix)]
  testcase_list = [os.path.join(test_dir, file) for file in testcase_list]
  testcase_list.sort()

  # open run.master and test every cmd
  with open(configuration_file, "r") as configuration_reader:
    utilities = configuration_reader.readlines()

    # process every line in configuration_file
    for line in utilities:
      line = line.strip()
      # skip empty line
      if(line == ""):
        continue

      # skip commented line
      if(line_commented(line)):
        print("%s" % line)
        continue

      # check syntax valid
      valid = line_syntax_valid(line)
      if(not valid):
        print("invalid syntax: %s" % line)
        with open(os.path.join(result_dir, "err"), "a") as err_writer:
          err_writer.write("invalid syntax: %s\n" % line)
        continue

      print("start testing: %s" % line)

      # parse the line
      cmd, test_type, utility_name, new_file_name, all_options_from_pool, log_name = parse_a_line(line)

      log_path = os.path.join(result_dir, log_name)

      if(test_type == "file"):
        run_file(cmd, utility_name, log_path, all_options_from_pool, testcase_list)
      elif(test_type == "stdin"):
        run_stdin(cmd, utility_name, log_path, all_options_from_pool, testcase_list)
      elif(test_type == "cp"):
        run_cp(cmd, utility_name, new_file_name, log_path, all_options_from_pool, testcase_list)
      elif(test_type == "two_files"):
        run_two_files(cmd, utility_name, log_path, all_options_from_pool, testcase_list)
      else:
        run_pty(cmd, utility_name, log_path, all_options_from_pool, testcase_list)

  fnull.close()




