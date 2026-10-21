import threading


class TableCreator(threading.Thread):
    def __init__(self, num):
        super().__init__()
        self.num = num

    def run(self):
        for i in range(1, 11):
            result = self.num * i
            print(f"{self.num} times {i} is {result}")


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
