import threading


class Counter:
    def __init__(self, initial_count):
        self._count = initial_count
        self._lock = threading.Lock()

    def incValue(self, offset):
        with self._lock:
            self._count += offset

    def getValue(self):
        with self._lock:
            return self._count

    def decValue(self, offset):
        with self._lock:
            self._count -= offset


# Function for concurrent increment operation
def concurrent_inc(counter, offset):
    for _ in range(1000):
        counter.incValue(offset)


# Function for concurrent decrement operation
def concurrent_dec(counter, offset):
    for _ in range(1000):
        counter.decValue(offset)


if __name__ == "__main__":
    counter = Counter(0)
    threads = []
    for _ in range(10):
        threads.append(threading.Thread(target=concurrent_inc, args=(counter, 1)))
        threads.append(threading.Thread(target=concurrent_dec, args=(counter, 1)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print("Final counter value:", counter.getValue())
