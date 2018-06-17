#!/usr/bin/python

import time
from subprocess import call

for i in range(30):
    cmd = "dd if=/dev/zero of=big-file-%s count=1024 bs=1048576" % i
    call(cmd.split(" "))
    time.sleep(2)

# https://stackoverflow.com/questions/8816059/create-file-of-particular-size-in-python
# creates files of 1GB size but `df -h` doesn't recognize that (not sure why).
