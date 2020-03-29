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

############
# options
# where are the test cases
test_dir = "../NewTest_big"

# the script will test all the files starting with a specified test_prefix
test_prefix = "t"

# if the cmd does not finish in timeout seconds, the test result will be considered as a hang
timeout = 300

# if there are hang_num successive hangs, no need to continue the testing on the current cmd
# check the way you use the cmd, or increase the timeout and retest, or consider the results as hangs
hang_num = 3

# the script will test each cmd in run.master on the test cases in test_dir
all_utilities_file = "./test_Linux/run.master_options"

# the result will be saved in output_dir, each cmd corresponds to a result file 
output_dir = "./results/linux_big"

# the script will combine result files into single file named combine_filename
combine_filename = "all"
############


# redirect the output to /dev/null, otherwise the shell will be overwhelmed by outputs
fnull = open(os.devnull, 'w')


# get path of all test cases
test_list = []
test_list = os.listdir(test_dir)
test_list = [file for file in test_list if file.startswith(test_prefix)]
test_list = [os.path.join(test_dir, file) for file in test_list]


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
      print(final_cmd)
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
      print(final_cmd)
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
      print(final_cmd)
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
def run_double(item, output, test_list, fnull, timeout): 
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
      print(final_cmd)
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
  # check if there is suffix
  #idx = item.find("[")

  # idx >= 0 when match "[" successfully
  #if idx >= 0:
  #  suffix = item[idx + 1: -1]
  #  item = item[0: idx]

  cmd_type = item.split(" ", 1)[0]
  cmd = item.split(" ", 1)[1]
  hang_count = 0
  retcode = 0

  for test_case in test_list:
    # if there are hang_num successive hangs, break
    if hang_count >= hang_num:
      break

    try:
      final_cmd = "./ptyjig/pty -d 0.001 " + cmd
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
      print(final_cmd)
      print(test_case)
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

test_dir = ''
output_dir = ''

try:
  opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["ifile=","ofile="])
except getopt.GetoptError:
  print ("python run.py -i <inputfile> -o <outputfile>")
  sys.exit(2)
for opt, arg in opts:
  if opt == '-h':
    print ("python test.py -i <inputfile> -o <outputfile>")
    sys.exit()
  elif opt in ("-i", "--ifile"):
    test_dir = arg
  elif opt in ("-o", "--ofile"):
    output_dir = arg
print ("Input file is ", test_dir)
print ("Output file is ", output_dir)

if not os.path.exists(output_dir):
  os.mkdir(output_dir)

# open run.master and test every cmd
with open(all_utilities_file, "r") as all_utilities_reader:
  utilities = all_utilities_reader.readlines()

  # process every line in all_utilities_file
  for item in utilities:
    item = item.strip()
    cmd_type = item.split(" ", 1)[0]
    print(item)

    if cmd_type == "run.stdin":
      cmd = item.split(" ", 1)[1]
      #print("h1")
      file_name = os.path.join(output_dir, "%s.%s" % (cmd_type, cmd.replace("/", "-")))
      if os.path.exists(file_name) and os.stat(file_name).st_size != 0:
        with open(file_name, "r") as f:
          if f.readlines()[-1] == "finished\n":
            continue
      output_file = open(file_name, "w")
      #print("h2")
      output_file.write("start: %s\n" % item)
      run_stdin(item, output_file, test_list, fnull, timeout)
      output_file.write("finished\n")
      output_file.close()

    elif cmd_type == "run.file":
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
    
    elif cmd_type == "run.pty":
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

    elif cmd_type == "run.cp":
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

    elif cmd_type == "run.double":
      cmd = item.split(" ", 1)[1]
      file_name = os.path.join(output_dir, "%s.%s" % (cmd_type, cmd.replace("/", "-")))
      if os.path.exists(file_name) and os.stat(file_name).st_size != 0:
        with open(file_name, "r") as f:
          if f.readlines()[-1] == "finished\n":
            continue
      output_file = open(file_name, "w")
      output_file.write("start: %s\n" % item)
      run_double(item, output_file, test_list, fnull, timeout)
      output_file.write("finished\n")
      output_file.close()

  all_utilities_reader.close()
  fnull.close()


# combine the result files
with open(combine_filename, "w") as file_to_write:
  dir = os.listdir(output_dir)
  dir.sort()
  for item in dir:
    with open(os.path.join(output_dir, item), "r") as file_to_read:
      file_to_write.write(file_to_read.read())



