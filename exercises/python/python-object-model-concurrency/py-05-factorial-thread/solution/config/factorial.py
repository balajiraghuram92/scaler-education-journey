import math
import threading


class FactorialThread(threading.Thread):
    def __init__(self, n):
        super().__init__()
        self.n = n
        self.result = None

    def run(self):
        self.result = math.factorial(self.n)


def compute_large_factorial(n):
    thread = FactorialThread(n)
    thread.start()
    thread.join()
    return thread.result
