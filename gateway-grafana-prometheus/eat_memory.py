#!/usr/bin/python

# based on https://stackoverflow.com/questions/6317818/how-to-eat-memory-using-python

import time

blanks = " "

try:
    for i in range(50):
        print(i)
        blanks += " " * (50 * 1000 * 1000)
        time.sleep(5)
except MemoryError:
    print("We're going out of memory.")
    time.sleep(10)
