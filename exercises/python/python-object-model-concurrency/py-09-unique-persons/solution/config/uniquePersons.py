class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age


def find_unique_persons(people):
    unique_names = set()
    unique_persons = []
    for person in people:
        if person.name not in unique_names:
            unique_names.add(person.name)
            unique_persons.append(person)
    return unique_persons
