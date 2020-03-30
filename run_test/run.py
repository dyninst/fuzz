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

# if there are hang_num successive hangs, no need to continue the testing on the current cmd
# check the way you use the cmd, or increase the timeout and retest, or consider the results as hangs
hang_num = 3

# the script will test each cmd in configuration_file on the test cases in test_dir
configuration_file = "./test_MacOS/run.master_options_debug"

# redirect the output to /dev/null, otherwise the shell will be overwhelmed by outputs
fnull = open(os.devnull, 'w')


# return a random subset of s, each element has 0.5 probability
def random_subset(s):
  out = ""
  for el in s:
    # random coin flip
    if random.random() > 0.5:
      out = out + el + " "
  return out


# run cmds with input from file
def run_file(item, output, test_list, fnull, timeout): 
  # check if there are options
  idx = item.find("[")

  # idx >= 0 when match "[" successfully
  if idx >= 0:
    options = item[idx + 1: -1]
    options = options.split()
    item = item[0: idx]

  cmd_type = item.split(" ", 1)[0]
  cmd = item.split(" ", 1)[1]
  hang_count = 0
  retcode = 0

  for test_case in test_list:
    # if there are hang_num successive hangs, break
    if hang_count >= hang_num:
      break

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

    except(subprocess.TimeoutExpired):
      hang_count = hang_count + 1
      output.write("%s %s hang\n" % (cmd_type, final_cmd))

    except(FileNotFoundError):
      output.write("%s %s not found\n" % (cmd_type, final_cmd))
      break

    else:
      hang_count = 0
      # check return value, record exit code with special meaning
      if retcode >= 126 or retcode < 0:
        output.write("%s %s error: %d\n" % (cmd_type, final_cmd, retcode))


# run cmds with input from file with specified extension name
def run_cp(item, output, test_list, fnull, timeout): 
  # check if there are options
  idx = item.find("[")

  # idx >= 0 when match "[" successfully
  if idx >= 0:
    options = item[idx + 1: -1]
    options = options.split()
    item = item[0: idx]

  cmd_type = item.split(" ", 2)[0]
  file_tmp = item.split(" ", 2)[1]
  cmd = item.split(" ", 2)[2]
  hang_count = 0
  retcode = 0

  for test_case in test_list:
    # if there are hang_num successive hangs, break
    if hang_count >= hang_num:
      break

    try:
      subprocess.call("cp %s %s" % (test_case, file_tmp), shell=True)
      final_cmd = cmd
      # if options exist, append options to the final_cmd
      if idx >= 0:
        options_random = random_subset(options)
        final_cmd = final_cmd + " " + options_random
      final_cmd = final_cmd + " " + file_tmp

      # print final_cmd to stdin
      print("running: ", final_cmd)

      retcode = subprocess.call(final_cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT, timeout=timeout)

    except(subprocess.TimeoutExpired):
      hang_count = hang_count + 1
      output.write("%s %s %s hang\n" % (cmd_type, final_cmd, test_case))

    except(FileNotFoundError):
      output.write("%s %s not found\n" % (cmd_type, final_cmd))
      break

    else:
      hang_count = 0
      # check return value, record exit code with special meaning
      if retcode >= 126 or retcode < 0:
        output.write("%s %s %s error: %d\n" % (cmd_type, final_cmd, test_case, retcode))
        subprocess.call("rm %s" % file_tmp, shell=True)


# run cmds with input from stdin
def run_stdin(item, output, test_list, fnull, timeout): 
  # check if there are options
  idx = item.find("[")

  # idx >= 0 when match "[" successfully
  if idx >= 0:
    options = item[idx + 1: -1]
    options = options.split()
    item = item[0: idx]

  cmd_type = item.split(" ", 1)[0]
  cmd = item.split(" ", 1)[1]
  hang_count = 0
  retcode = 0

  for test_case in test_list:
    # if there are hang_num successive hangs, break
    if hang_count >= hang_num:
      break

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

    except(subprocess.TimeoutExpired):
      hang_count = hang_count + 1
      output.write("%s %s hang\n" % (cmd_type, final_cmd))

    except(FileNotFoundError):
      output.write("%s %s not found\n" % (cmd_type, final_cmd))
      break

    else:
      hang_count = 0
      # check return value, record exit code with special meaning
      if retcode >= 126 or retcode < 0:
        output.write("%s %s error: %d\n" % (cmd_type, final_cmd, retcode))

# run cmds with two input files
def run_two_files(item, output, test_list, fnull, timeout): 
  # check if there are options
  idx = item.find("[")

  # idx >= 0 when match "[" successfully
  if idx >= 0:
    options = item[idx + 1: -1]
    options = options.split()
    item = item[0: idx]

  cmd_type = item.split(" ", 1)[0]
  cmd = item.split(" ", 1)[1]
  hang_count = 0
  retcode = 0

  for i in range(len(test_list)):
    # if there are hang_num successive hangs, break
    if hang_count >= hang_num:
      break

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

    except(subprocess.TimeoutExpired):
      hang_count = hang_count + 1
      output.write("%s %s hang\n" % (cmd_type, final_cmd))

    except(FileNotFoundError):
      output.write("%s %s not found\n" % (cmd_type, final_cmd))
      break

    else:
      hang_count = 0
      # check return value, record exit code with special meaning
      if retcode >= 126 or retcode < 0:
        output.write("%s %s error: %d\n" % (cmd_type, final_cmd, retcode))


def run_pty(item, output, test_list, fnull, timeout):

  cmd_type = item.split(" ", 1)[0]
  cmd = item.split(" ", 1)[1]
  hang_count = 0
  retcode = 0

  for test_case in test_list:
    # if there are hang_num successive hangs, break
    if hang_count >= hang_num:
      break

    try:
      final_cmd = "../src/pty -d 0.001 " + cmd
      # if options exist, append options to the final_cmd
      #if idx >= 0:
      #  options_random = random_subset(options)
      #  final_cmd = final_cmd + " " + options_random
      subprocess.call("cat %s ./ptyjig/end/end_%s > tmp" % (test_case, cmd), shell=True, stdout=fnull, stderr=subprocess.STDOUT)
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
    except(subprocess.TimeoutExpired):
      hang_count = hang_count + 1
      output.write("%s %s %s hang\n" % (cmd_type, final_cmd, test_case))

    except(FileNotFoundError):
      output.write("%s %s not found\n" % (cmd_type, final_cmd))
      break

    else:
      hang_count = 0
      # check return value, record exit code with special meaning
      if retcode >= 126 or retcode < 0:
        output.write("%s %s %s error: %d\n" % (cmd_type, final_cmd, test_case, retcode))
        subprocess.call("rm tmp", shell=True)



# the script start here
# create dir for log

if __name__ == "__main__":

  # options

  # where are the test cases
  test_dir = "../NewTest_small"

  # the result will be saved in output_dir, each cmd corresponds to a result file 
  output_dir = "./results/linux_small"

  # the script will test all the files starting with a specified prefix. Prefix is empty string by default, 
  # which means all the files in test_dir will be tested.
  prefix = ""

  # if the cmd does not finish in timeout(300 by default) seconds, the test result will be considered as a hang
  timeout = 300

  try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:o:p:t:",["help", "ifile=", "ofile=", "prefix=", "timeout="])
  except getopt.GetoptError:
    print("usage: python3 run.py -p <prefix> -t <timeout> -i <inputfile> -o <outputfile>")
    sys.exit(2)

  for opt, arg in opts:
    if opt in ("-h", "--help"):
      print("usage: python3 run.py -p <prefix> -t <timeout> -i <inputfile> -o <outputfile>")
      sys.exit()
    elif opt in ("-i", "--ifile"):
      test_dir = arg
    elif opt in ("-o", "--ofile"):
      output_dir = arg
    elif opt in ("-p", "--prefix"):
      prefix = arg
    elif opt in ("-t", "--timeout"):
      print(arg)
      timeout = int(arg)

  print("Input file is ", test_dir)
  print("Output file is ", output_dir)
  print("configuration file is ", configuration_file)
  print("Prefix is ", prefix)
  print("Timeout is ", timeout)

  # make directory to save output
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)

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
        file_name = os.path.join(output_dir, "%s.%s" % (cmd_type, cmd.replace("/", "-")))
        if os.path.exists(file_name) and os.stat(file_name).st_size != 0:
          with open(file_name, "r") as f:
            if f.readlines()[-1] == "finished\n":
              continue
        output_file = open(file_name, "w")
        output_file.write("start: %s\n" % item)
        run_stdin(item, output_file, test_list, fnull, timeout)
        output_file.write("finished\n")
        output_file.close()

      # file
      elif cmd_type == "file":
        cmd = item.split(" ", 1)[1]
        file_name = os.path.join(output_dir, "%s.%s" % (cmd_type, cmd.replace("/", "-")))
        if os.path.exists(file_name) and os.stat(file_name).st_size != 0:
          with open(file_name, "r") as f:
            if f.readlines()[-1] == "finished\n":
              continue
        output_file = open(file_name, "w")
        output_file.write("start: %s\n" % item)
        run_file(item, output_file, test_list, fnull, timeout)
        output_file.write("finished\n")
        output_file.close()
      
      # pty
      elif cmd_type == "pty":
        cmd = item.split(" ", 1)[1]
        file_name = os.path.join(output_dir, "%s.%s" % (cmd_type, cmd.replace("/", "-")))
        if os.path.exists(file_name) and os.stat(file_name).st_size != 0:
          with open(file_name, "r") as f:
            if f.readlines()[-1] == "finished\n":
              continue
        output_file = open(file_name, "w")
        output_file.write("start: %s\n" % item)
        run_pty(item, output_file, test_list, fnull, timeout)
        output_file.write("finished\n")
        output_file.close()

      # cp
      elif cmd_type == "cp":
        cmd = item.split(" ", 2)[2]
        file_name = os.path.join(output_dir, "%s.%s" % (cmd_type, cmd.replace("/", "-")))
        if os.path.exists(file_name) and os.stat(file_name).st_size != 0:
          with open(file_name, "r") as f:
            if f.readlines()[-1] == "finished\n":
              continue
        output_file = open(file_name, "w")
        output_file.write("start: %s\n" % item)
        run_cp(item, output_file, test_list, fnull, timeout)
        output_file.write("finished\n")
        output_file.close()

      # two_files
      elif cmd_type == "two_files":
        cmd = item.split(" ", 1)[1]
        file_name = os.path.join(output_dir, "%s.%s" % (cmd_type, cmd.replace("/", "-")))
        if os.path.exists(file_name) and os.stat(file_name).st_size != 0:
          with open(file_name, "r") as f:
            if f.readlines()[-1] == "finished\n":
              continue
        output_file = open(file_name, "w")
        output_file.write("start: %s\n" % item)
        run_two_files(item, output_file, test_list, fnull, timeout)
        output_file.write("finished\n")
        output_file.close()

  fnull.close()




