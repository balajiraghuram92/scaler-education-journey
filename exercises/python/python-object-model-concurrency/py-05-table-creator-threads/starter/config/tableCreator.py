import threading


class TableCreator(threading.Thread):
    """A thread that prints the multiplication table of one number.

    - ``__init__(self, num)`` calls ``super().__init__()`` and stores ``num``
    - ``run()`` prints ten lines, one ``print`` call each, for ``i`` from 1 to 10 in the exact
      format ``<num> times <i> is <result>``, for example ``3 times 4 is 12``
    - zero and negative numbers work too (``-3 times 2 is -6``)
    """

    def __init__(self, num):
        raise NotImplementedError("Implement TableCreator.__init__")

    def run(self):
        raise NotImplementedError("Implement TableCreator.run")


class Client:
    @staticmethod
    def main():
        n = int(input("Enter a number: "))

        threads = []
        for i in range(1, n + 1):
            thread = TableCreator(i)
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
