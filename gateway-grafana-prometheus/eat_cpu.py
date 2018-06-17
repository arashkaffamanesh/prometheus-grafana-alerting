#!/usr/bin/python

# based on https://technobeans.com/2012/04/16/5-ways-of-fibonacci-in-python/

N = 50

def fibonacci(n):
    if n in (1, 2):
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(N)
