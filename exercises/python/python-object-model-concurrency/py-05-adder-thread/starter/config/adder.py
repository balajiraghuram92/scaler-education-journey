import threading


class Adder(threading.Thread):
    """A thread that prints the sum of two numbers.

    - ``__init__(self, num1, num2)`` calls ``super().__init__()`` and stores both numbers
    - ``run()`` prints ``num1 + num2`` (just the number, followed by a newline)
    """

    def __init__(self, num1, num2):
        raise NotImplementedError("Implement Adder.__init__")

    def run(self):
        raise NotImplementedError("Implement Adder.run")


class Client:
    @staticmethod
    def main():
        """Read two integers with ``input("Enter the first number: ")`` and
        ``input("Enter the second number: ")``, start an ``Adder`` thread and ``join()`` it so the
        output appears before ``main`` returns."""
        raise NotImplementedError("Implement Client.main")
