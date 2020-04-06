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

# define variables
return_value = 126
float_rand = 0.5
index_num = 2
arg_num = 6

# redirect the output to /dev/null, otherwise the shell will be overwhelmed by outputs
fnull = open(os.devnull, 'w')
ptyjig_path = "../src/ptyjig"
# ptyjig_delay = 0.001

# return a random subset of s, each element has 0.5 probability
def random_subset(s):
  out = ""
  for el in s:
    # random coin flip
    if random.random() > float_rand:
      out = out + el + " "
  return out

def parse_a_line(line, testcase, testcase_list):

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

  # get the options in option pool
  all_options_from_pool = line.split("#")[1]

  # get the final_cmd that can be run
  # part_of_line is the part behind utility name
  if(test_type == "cp"):
    part_of_line = line.split("", 3)[3]
  else:
    part_of_line = line.split("", 2)[2]

  if(test_type == "stdin"):
    final_cmd = utility_name 
              + " " + part_of_line.split("#")[0]
              + " " + "%s" 
              + " " + part_of_line.split("#")[2]
              + " < " + testcase

  elif(test_type == "file"):
    final_cmd = utility_name 
              + " " + part_of_line.split("#")[0]
              + " " + "%s" 
              + " " + part_of_line.split("#")[2]
              + " " + testcase

  elif(test_type == "cp"):
    final_cmd = utility_name 
              + " " + part_of_line.split("#")[0]
              + " " + "%s" 
              + " " + part_of_line.split("#")[2]
              + " " + new_file_name

  elif(test_type == "two_files"):
    test_case1 = random.choice(test_list)
    test_case2 = random.choice(test_list)
    final_cmd = utility_name 
              + " " + part_of_line.split("#")[0]
              + " " + "%s" 
              + " " + part_of_line.split("#")[2]
              + " " + test_case1
              + " " + test_case2

  elif(test_type == "pty"):
    test_case1 = random.choice(test_list)
    test_case2 = random.choice(test_list)
    final_cmd = ptyjig_path
              # -d delay will be set in test_pty
              + " " + "-d" + " " + "%f"
              + " " + utility_name
              + " " + part_of_line.split("#")[0] 
              + " " + "%s" 
              + " " + part_of_line.split("#")[2]
              + " < " + new_file_name

  log_name = "%s.%s" % (utility_name, test_type)

  return final_cmd, test_type, utility_name, new_file_name, all_options_from_pool, log_name



# run "file"
def test_file(final_cmd, utility_name, log_writer, options_sampled_from_pool): 

  # print final_cmd to stdin
  final_cmd = final_cmd % options_sampled_from_pool
  print("running: ", final_cmd)

  ret = 0

  try:
    retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)

  except(subprocess.TimeoutExpired):
    log_writer.write("%s hang\n" % final_cmd)

  except(FileNotFoundError):
    log_writer.write("%s not found\n" % utility_name)
    ret = -1

  else:
    # check return value, record exit code with special meaning
    if retcode >= return_value or retcode < 0:
      log_writer.write("%s failed, error: %d\n" % (final_cmd, retcode))

  finally:
    return ret

# run "stdin", so far it's identical to test_file
def test_stdin(final_cmd, utility_name, log_writer, options_sampled_from_pool): 

  # print final_cmd to stdin
  final_cmd = final_cmd % options_sampled_from_pool
  print("running: ", final_cmd)

  ret = 0

  try:
    retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)

  except(subprocess.TimeoutExpired):
    log_writer.write("%s hang\n" % final_cmd)

  except(FileNotFoundError):
    log_writer.write("%s not found\n" % utility_name)
    ret = -1

  else:
    # check return value, record exit code with special meaning
    if retcode >= return_value or retcode < 0:
      log_writer.write("%s failed, error: %d\n" % (final_cmd, retcode))

  finally:
    return ret

# run "cp", need to copy test case firstly
def test_cp(final_cmd, utility_name, new_file_name, test_case, log_writer, options_sampled_from_pool): 

  # print final_cmd to stdin
  final_cmd = final_cmd % options_sampled_from_pool
  print("running: ", final_cmd)

  ret = 0

  # copy test case to a new temporary file with a specified name
  subprocess.call(["cp %s %s" % (test_case, new_file_name)], shell=True)

  try:
    retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)

  except(subprocess.TimeoutExpired):
    log_writer.write("%s hang\n" % final_cmd)

  except(FileNotFoundError):
    log_writer.write("%s not found\n" % utility_name)
    ret = -1

  else:
    # check return value, record exit code with special meaning
    if retcode >= return_value or retcode < 0:
      log_writer.write("%s failed, error: %d\n" % (final_cmd, retcode))

  finally:
    subprocess.call("rm %s" % new_file_name, shell=True)
    return ret

# run "two_files", so far it's identical to test_file
def test_two_files(final_cmd, utility_name, log_writer, options_sampled_from_pool): 

  # print final_cmd to stdin
  final_cmd = final_cmd % options_sampled_from_pool
  print("running: ", final_cmd)

  ret = 0

  try:
    retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)

  except(subprocess.TimeoutExpired):
    log_writer.write("%s hang\n" % final_cmd)

  except(FileNotFoundError):
    log_writer.write("%s not found\n" % utility_name)
    ret = -1

  else:
    # check return value, record exit code with special meaning
    if retcode >= return_value or retcode < 0:
      log_writer.write("%s failed, error: %d\n" % (final_cmd, retcode))

  finally:
    return ret

# run "pty"
def test_pty(final_cmd, utility_name, test_case, log_writer, options_sampled_from_pool): 

  # copy test case to tmp and append the designed end file 
  subprocess.call("cat %s ./end/end_%s > tmp" % (testcase_list, utility_name), shell=True, stdout=fnull, stderr=subprocess.STDOUT)

  # remove all ^z in tmp
  fr = open("tmp", "rb")
  s = fr.read()
  fr.close()
  s = s.replace(b"\x1a", b"")

  # Z or z will suspend telnet 
  if(cmd == "telnet"):
      s = s.replace(b"Z", b"")
      s = s.replace(b"z", b"")
  fw = open("tmp", "wb")
  fw.write(s)
  fw.close()

  # htop needs to be fed input slowly, otherwise it can't quit
  if(utility_name == "htop"):
    final_cmd = final_cmd % (0.05, options_sampled_from_pool)
  else:
    final_cmd = final_cmd % (0.001, options_sampled_from_pool)

  # print final_cmd to stdin
  print("running: ", final_cmd)

  ret = 0

  try:
    retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)

  except(subprocess.TimeoutExpired):
    log_writer.write("%s hang\n" % final_cmd)

  except(FileNotFoundError):
    log_writer.write("%s not found\n" % utility_name)
    ret = -1

  else:
    # check return value, record exit code with special meaning
    if retcode >= return_value or retcode < 0:
      log_writer.write("%s failed, error: %d\n" % (final_cmd, retcode))

  finally:
    return ret



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

  if len(sys.argv) < arg_num:
     print("Usage: python3 run.py [configuration_file] [-i inputfile] [-o outputfile]")
     sys.exit(2)

  configuration_file = sys.argv[1]

  try:
    opts, args = getopt.getopt(sys.argv[2:],"hi:o:p:t:",["ifile=", "ofile=", "prefix=", "timeout="])
  except getopt.GetoptError as err:
    print("Usage: python3 run.py configuration_file -i inputfile [-p prefix] [-t timeout] [-o outputfile]")
    sys.exit(2)

  for opt, arg in opts:
    if opt in ("-h", "--help"):
      print("Usage: python3 run.py configuration_file -i inputfile [-p prefix] [-t timeout] [-o outputfile]")
      sys.exit(2)
    elif opt in ("-i", "--ifile"):
      test_dir = arg
    elif opt in ("-o", "--ofile"):
      result_dir = arg
    elif opt in ("-p", "--prefix"):
      prefix = arg
    elif opt in ("-t", "--timeout"):
      timeout = int(arg)

  if test_dir == "" or result_dir == "":
    print("Usage: python3 run.py configuration_file -i inputfile [-p prefix] [-t timeout] [-o outputfile]")
    sys.exit(2)

  # print out the parameters
  print("Input file is ", test_dir)
  print("Output file is ", result_dir)
  print("configuration file is ", configuration_file)
  print("Prefix is ", prefix)
  print("Timeout is ", timeout)

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
      print("start testing: ", line)

      # parse the line
      final_cmd, test_type, utility_name, new_file_name, all_options_from_pool, log_name = parse_a_line(line, testcase, testcase_list)

      # if the log exists and have been finished, go to test the next utility
      if os.path.exists(log_name) and os.stat(log_name).st_size != 0:
        with open(log_name, "r") as f:
          if f.readlines()[-1] == "finished\n":
            break

      # otherwise, create the log or overwrite it 
      log_writer = open(log_name, "w")
      log_writer.write("start: %s\n" % line)

      for testcase in testcase_list:
        options_sampled_from_pool = random_subset(all_options_from_pool.split())

        if(test_type == "file"):
          test_file(final_cmd, utility_name, log_writer, options_sampled_from_pool)
        elif(test_type == "stdin"):
          test_stdin(final_cmd, utility_name, log_writer, options_sampled_from_pool)
        elif(test_type == "cp"):
          test_cp(final_cmd, utility_name, new_file_name, test_case, log_writer, options_sampled_from_pool)
        elif(test_type == "two_files"):
          test_two_files(final_cmd, utility_name, log_writer, options_sampled_from_pool)
        elif(test_type == "pty"):
          test_pty(final_cmd, utility_name, test_case, log_writer, options_sampled_from_pool)
        else:
          if(line.startswith("//")):
            break
          else:
            print("unknown type: %s", test_type)
            break

      log_writer.write("finished\n")
      log_writer.close()
      print("finished: ", line)

  fnull.close()




