#  Copyright (c) 2020 Emma He, Mengxiao Zhang, Barton Miller
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

# this script is used to generate medium test cases.

import os, sys, re
import subprocess
import random
import time

fnull = open(os.devnull, 'w')
path = "./NewTest_medium2"

if not os.path.exists(path):
  os.mkdir(path)


# -0
for i in range(0, 100):
  print(i)
  if os.path.isfile(os.path.join(path, "t%d" % i)):
    continue
  # sleep more than 1 second to prevent fuzz from using the same random seed as the previous one.
  time.sleep(1.1)
  subprocess.call(["fuzz", "-0", "-o", os.path.join(path, "t%d" % i)], stdout=fnull, stderr=subprocess.STDOUT)

start = 100


# -a
for i in range(start, start+100):
  print(i)
  if os.path.isfile(os.path.join(path, "t%d" % i)):
    continue
  time.sleep(1.1)
  subprocess.call(["fuzz", "-a", "-o", os.path.join(path, "t%d" % i)], stdout=fnull, stderr=subprocess.STDOUT)
start = start + 100

# -p
for i in range(start, start+100):
  print(i)
  if os.path.isfile(os.path.join(path, "t%d" % i)):
    continue
  time.sleep(1.1)
  subprocess.call(["fuzz", "-p", "-o", os.path.join(path, "t%d" % i)], stdout=fnull, stderr=subprocess.STDOUT)
start = start + 100

# -0 + -l
for i in range(start, start+100):
  print(i)
  if os.path.isfile(os.path.join(path, "t%d" % i)):
    continue
  time.sleep(1.1)
  l = random.randint(1, 255)
  subprocess.call(["fuzz", "-l %d" % l, "-0", "-o", os.path.join(path, "t%d" % i)], stdout=fnull, stderr=subprocess.STDOUT)
start = start + 100

# -a + -l
for i in range(start, start+100):
  print(i)
  if os.path.isfile(os.path.join(path, "t%d" % i)):
    continue
  time.sleep(1.1)
  l = random.randint(1, 255)
  subprocess.call(["fuzz", "-l %d" % l, "-a", "-o", os.path.join(path, "t%d" % i)], stdout=fnull, stderr=subprocess.STDOUT)
start = start + 100

# -p + -l
for i in range(start, start+100):
  print(i)
  if os.path.isfile(os.path.join(path, "t%d" % i)):
    continue
  time.sleep(1.1)
  l = random.randint(1, 255)
  subprocess.call(["fuzz", "-l %d" % l, "-p", "-o", os.path.join(path, "t%d" % i)], stdout=fnull, stderr=subprocess.STDOUT)
start = start + 100

# -0 + -l + 5000
for i in range(start, start+100):
  print(i)
  if os.path.isfile(os.path.join(path, "t%d" % i)):
    continue
  time.sleep(1.1)
  l = random.randint(1, 255)
  n = random.randint(1, 5000)
  subprocess.call(["fuzz", "%d" % n, "-l %d" % l, "-0", "-o", os.path.join(path, "t%d" % i)], stdout=fnull, stderr=subprocess.STDOUT)
start = start + 100

# -a + -l + 5000
for i in range(start, start+100):
  print(i)
  if os.path.isfile(os.path.join(path, "t%d" % i)):
    continue
  time.sleep(1.1)
  l = random.randint(1, 255)
  n = random.randint(1, 5000)
  subprocess.call(["fuzz", "%d" % n, "-l %d" % l, "-a", "-o", os.path.join(path, "t%d" % i)], stdout=fnull, stderr=subprocess.STDOUT)
start = start + 100

# -p + -l + 5000
for i in range(start, start+100):
  print(i)
  if os.path.isfile(os.path.join(path, "t%d" % i)):
    continue
  time.sleep(1.1)
  l = random.randint(1, 255)
  n = random.randint(1, 5000)
  subprocess.call(["fuzz", "%d" % n, "-l %d" % l, "-p", "-o", os.path.join(path, "t%d" % i)], stdout=fnull, stderr=subprocess.STDOUT)
