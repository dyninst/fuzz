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

# return a random subset of s, each element has 0.5 probability
def random_subset(s):
  out = ""
  for el in s:
    # random coin flip
    if random.random() > float_rand:
      out = out + el + " "
  return out

# run cmds with input from file
def test_file(item, output, test_list, fnull, timeout): 
  # check if there are options
  idx = item.find("[")

  # idx >= 0 when match "[" successfully
  if idx >= 0:
    options = item[idx + 1: -1]
    options = options.split()
    item = item[0: idx]

  cmd_type = item.split(" ", 1)[0]
  cmd = item.split(" ", 1)[1]
  retcode = 0

  for test_case in test_list:
    try:
      final_cmd = cmd
      # if options exist, append options to the final_cmd
      if idx >= 0:
        options_random = random_subset(options)
        final_cmd = final_cmd + " " + options_random
      final_cmd = final_cmd + " " + test_case

      # print final_cmd to stdin
      print("running: ", final_cmd)

      retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)
      # retcode = subprocess.call(final_cmd, shell=True, timeout=timeout)

    except(subprocess.TimeoutExpired):
      output.write("%s %s hang\n" % (cmd_type, final_cmd))

    except(FileNotFoundError):
      output.write("%s %s not found\n" % (cmd_type, final_cmd))
      break

    else:
      # check return value, record exit code with special meaning
      if retcode >= return_value or retcode < 0:
        output.write("%s %s error: %d\n" % (cmd_type, final_cmd, retcode))

# run cmds with input from file with specified extension name
def test_cp(item, output, test_list, fnull, timeout): 
  # check if there are options
  idx = item.find("[")

  # idx >= 0 when match "[" successfully
  if idx >= 0:
    options = item[idx + 1: -1]
    options = options.split()
    item = item[0: idx]

  cmd_type = item.split(" ", index_num)[0]
  file_tmp = item.split(" ", index_num)[1]
  cmd = item.split(" ", index_num)[index_num]
  retcode = 0

  for test_case in test_list:
    try:
      subprocess.call(["cp %s %s" % (test_case, file_tmp)], shell=True)
      final_cmd = cmd
      # if options exist, append options to the final_cmd
      if idx >= 0:
        options_random = random_subset(options)
        final_cmd = final_cmd + " " + options_random
      final_cmd = final_cmd + " " + file_tmp + " " + test_case

      # print final_cmd to stdin
      print("running: ", final_cmd)

      retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)
      # retcode = subprocess.call(final_cmd, shell=True, timeout=timeout)

    except(subprocess.TimeoutExpired):
      output.write("%s %s %s hang\n" % (cmd_type, final_cmd, test_case))

    except(FileNotFoundError):
      output.write("%s %s not found\n" % (cmd_type, final_cmd))
      break

    else:
      # check return value, record exit code with special meaning
      if retcode >= return_value or retcode < 0:
        output.write("%s %s %s error: %d\n" % (cmd_type, final_cmd, test_case, retcode))
        subprocess.call("rm %s" % file_tmp, shell=True)


# run cmds with input from stdin
def test_stdin(item, output, test_list, fnull, timeout): 
  # check if there are options
  idx = item.find("[")

  # idx >= 0 when match "[" successfully
  if idx >= 0:
    options = item[idx + 1: -1]
    options = options.split()
    item = item[0: idx]

  cmd_type = item.split(" ", 1)[0]
  cmd = item.split(" ", 1)[1]
  retcode = 0

  for test_case in test_list:
    try:
      final_cmd = cmd
      # if options exist, append options to the final_cmd
      if idx >= 0:
        options_random = random_subset(options)
        final_cmd = final_cmd + " " + options_random
      final_cmd = final_cmd + " < " + test_case

      # print final_cmd to stdin
      print("running: ", final_cmd)

      retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)
      # retcode = subprocess.call(final_cmd, shell=True, timeout=timeout)

    except(subprocess.TimeoutExpired):
      output.write("%s %s hang\n" % (cmd_type, final_cmd))

    except(FileNotFoundError):
      output.write("%s %s not found\n" % (cmd_type, final_cmd))
      break

    else:
      # check return value, record exit code with special meaning
      if retcode >= return_value or retcode < 0:
        output.write("%s %s error: %d\n" % (cmd_type, final_cmd, retcode))

# run cmds with two input files
def test_two_files(item, output, test_list, fnull, timeout): 
  # check if there are options
  idx = item.find("[")

  # idx >= 0 when match "[" successfully
  if idx >= 0:
    options = item[idx + 1: -1]
    options = options.split()
    item = item[0: idx]

  cmd_type = item.split(" ", 1)[0]
  cmd = item.split(" ", 1)[1]
  retcode = 0

  for i in range(len(test_list)):
    try:
      test_case1 = random.choice(test_list)
      test_case2 = random.choice(test_list)

      final_cmd = cmd
      # if options exist, append options to the final_cmd
      if idx >= 0:
        options_random = random_subset(options)
        final_cmd = final_cmd + " " + options_random
      final_cmd = final_cmd + " " + test_case1 + " " + test_case2

      # print final_cmd to stdin
      print("running: ", final_cmd)

      retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)
      # retcode = subprocess.call(final_cmd, shell=True, timeout=timeout)

    except(subprocess.TimeoutExpired):
      output.write("%s %s hang\n" % (cmd_type, final_cmd))

    except(FileNotFoundError):
      output.write("%s %s not found\n" % (cmd_type, final_cmd))
      break

    else:
      # check return value, record exit code with special meaning
      if retcode >= return_value or retcode < 0:
        output.write("%s %s error: %d\n" % (cmd_type, final_cmd, retcode))


def test_pty(item, output, test_list, fnull, timeout):

  cmd_type = item.split(" ", 1)[0]
  cmd = item.split(" ", 1)[1]
  retcode = 0

  for test_case in test_list:
    try:
      final_cmd = "../src/pty_cross_platform -d 0.001 " + cmd
      subprocess.call("cat %s ./end/end_%s > tmp" % (test_case, cmd), shell=True, stdout=fnull, stderr=subprocess.STDOUT)
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

      final_cmd = final_cmd + " < " + "tmp"

      # print final_cmd to stdin
      print("running: ", final_cmd)

      retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)
      # retcode = subprocess.call(final_cmd, shell=True, timeout=timeout)

    except(subprocess.TimeoutExpired):
      output.write("%s %s %s hang\n" % (cmd_type, final_cmd, test_case))

    except(FileNotFoundError):
      output.write("%s %s not found\n" % (cmd_type, final_cmd))
      break

    else:
      # check return value, record exit code with special meaning
      if retcode >= return_value or retcode < 0:
        output.write("%s %s %s error: %d\n" % (cmd_type, final_cmd, test_case, retcode))
        subprocess.call("rm tmp", shell=True)

# the script start here
# create dir for log

if __name__ == "__main__":

  # options

  # where are the test cases
  test_dir = ""

  # the result will be saved in output_dir, each cmd corresponds to a result file 
  result_dir = ""

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
    print("Usage: python3 run.py [configuration_file] [-i inputfile] [-o outputfile]")
    sys.exit(2)

  for opt, arg in opts:
    if opt in ("-h", "--help"):
      print("Usage: python3 run.py [configuration_file] [-i inputfile] [-o outputfile]")
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
    print("Usage: python3 run.py [configuration_file] [-i inputfile] [-o outputfile]")
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
  test_list = []
  test_list = os.listdir(test_dir)
  test_list = [file for file in test_list if file.startswith(prefix)]
  test_list = [os.path.join(test_dir, file) for file in test_list]

  # open run.master and test every cmd
  with open(configuration_file, "r") as configuration_reader:
    utilities = configuration_reader.readlines()

    # process every line in configuration_file
    for item in utilities:
      print("start testing: ", item)

      item = item.strip()
      cmd_type = item.split(" ", 1)[0]
      
      # stdin
      if cmd_type == "stdin":
        cmd = item.split(" ", 1)[1]
        cmd_name = item.split(" ", 2)[1]
        # the filename to be saved as
        file_name = os.path.join(result_dir, "%s.%s" % (cmd_type, cmd_name))

        # if file exists, check if it is finished
        if os.path.exists(file_name):
          with open(file_name, "r") as f:
            if f.readlines()[-1] == "finished\n":
              continue
        output_file = open(file_name, "w")
        output_file.write("start: %s\n" % item)
        test_stdin(item, output_file, test_list, fnull, timeout)
        output_file.write("finished\n")
        output_file.close()

      # file
      elif cmd_type == "file":
        cmd = item.split(" ", 1)[1]
        cmd_name = item.split(" ", 2)[1]
        # the filename to be saved as
        file_name = os.path.join(result_dir, "%s.%s" % (cmd_type, cmd_name))

        # if file exists, check if it is finished
        if os.path.exists(file_name):
          with open(file_name, "r") as f:
            if f.readlines()[-1] == "finished\n":
              continue
        output_file = open(file_name, "w")
        output_file.write("start: %s\n" % item)
        test_file(item, output_file, test_list, fnull, timeout)
        output_file.write("finished\n")
        output_file.close()
      
      # pty
      elif cmd_type == "pty":
        cmd = item.split(" ", 1)[1]
        cmd_name = item.split(" ", 2)[1]
        # the filename to be saved as
        file_name = os.path.join(result_dir, "%s.%s" % (cmd_type, cmd_name))

        # if file exists, check if it is finished
        if os.path.exists(file_name):
          with open(file_name, "r") as f:
            if f.readlines()[-1] == "finished\n":
              continue
        output_file = open(file_name, "w")
        output_file.write("start: %s\n" % item)
        test_pty(item, output_file, test_list, fnull, timeout)
        output_file.write("finished\n")
        output_file.close()

      # cp
      elif cmd_type == "cp":
        cmd = item.split(" ", 2)[2]
        cmd_name = item.split(" ", 3)[2]
        # the filename to be saved as
        file_name = os.path.join(result_dir, "%s.%s" % (cmd_type, cmd_name))

        # if file exists, check if it is finished
        if os.path.exists(file_name):
          with open(file_name, "r") as f:
            if f.readlines()[-1] == "finished\n":
              continue
        output_file = open(file_name, "w")
        output_file.write("start: %s\n" % item)
        test_cp(item, output_file, test_list, fnull, timeout)
        output_file.write("finished\n")
        output_file.close()

      # two_files
      elif cmd_type == "two_files":
        cmd = item.split(" ", 1)[1]
        cmd_name = item.split(" ", 2)[1]
        # the filename to be saved as
        file_name = os.path.join(result_dir, "%s.%s" % (cmd_type, cmd_name))

        # if file exists, check if it is finished
        if os.path.exists(file_name):
          with open(file_name, "r") as f:
            if f.readlines()[-1] == "finished\n":
              continue
        output_file = open(file_name, "w")
        output_file.write("start: %s\n" % item)
        test_two_files(item, output_file, test_list, fnull, timeout)
        output_file.write("finished\n")
        output_file.close()

  fnull.close()




