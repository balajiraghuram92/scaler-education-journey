import threading


class Foo:
    def __init__(self):
        self.semaphore_second = threading.Semaphore(0)
        self.semaphore_third = threading.Semaphore(0)
        # output will store the string values added by each function call
        self.output = []

    def first(self):
        self.output.append("first")
        self.semaphore_second.release()

    def second(self):
        self.semaphore_second.acquire()
        self.output.append("second")
        self.semaphore_third.release()

    def third(self):
        self.semaphore_third.acquire()
        self.output.append("third")


if __name__ == "__main__":
    foo = Foo()
    threads = [threading.Thread(target=getattr(foo, name)) for name in ("third", "second", "first")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print("Output sequence:", foo.output)
