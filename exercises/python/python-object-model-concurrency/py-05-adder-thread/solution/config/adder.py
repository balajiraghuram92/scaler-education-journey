import threading


class Adder(threading.Thread):
    def __init__(self, num1, num2):
        super().__init__()
        self.num1 = num1
        self.num2 = num2

    def run(self):
        result = self.num1 + self.num2
        print(result)


class Client:
    @staticmethod
    def main():
        num1 = int(input("Enter the first number: "))
        num2 = int(input("Enter the second number: "))

        adder_thread = Adder(num1, num2)
        adder_thread.start()
        adder_thread.join()
