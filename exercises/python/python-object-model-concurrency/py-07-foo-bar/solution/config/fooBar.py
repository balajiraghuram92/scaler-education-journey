import threading


class FooBar:
    def __init__(self, n):
        self.n = n
        self.foo_sem = threading.Semaphore(1)
        self.bar_sem = threading.Semaphore(0)

    def foo(self):
        for _ in range(self.n):
            self.foo_sem.acquire()
            print("foo", end='')
            self.bar_sem.release()

    def bar(self):
        for _ in range(self.n):
            self.bar_sem.acquire()
            print("bar", end='')
            self.foo_sem.release()


if __name__ == "__main__":
    fb = FooBar(5)
    threads = [threading.Thread(target=fb.foo), threading.Thread(target=fb.bar)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print()
