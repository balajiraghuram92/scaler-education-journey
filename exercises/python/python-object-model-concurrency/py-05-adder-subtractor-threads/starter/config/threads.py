import threading


class Adder(threading.Thread):
    """``run()`` prints ``I am the Adder class``."""

    def run(self):
        raise NotImplementedError("Implement Adder.run")


class Subtractor(threading.Thread):
    """``run()`` prints ``I am the Subtractor class``."""

    def run(self):
        raise NotImplementedError("Implement Subtractor.run")


class Client:
    @staticmethod
    def main():
        """Print ``I am the main class``, create one ``Adder`` and one ``Subtractor``, start BOTH,
        then join both before returning."""
        raise NotImplementedError("Implement Client.main")
