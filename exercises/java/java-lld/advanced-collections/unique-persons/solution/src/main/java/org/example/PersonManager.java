package org.example;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

public class PersonManager {
    public static List<Person> removeDuplicatePersons(List<Person> persons) {
        HashSet<String> seenNames = new HashSet<>();
        List<Person> uniquePersons = new ArrayList<>();

        if(persons==null) return uniquePersons;
        for (Person person : persons) {
            if (!seenNames.contains(person.getName())) {
                seenNames.add(person.getName());
                uniquePersons.add(person);
            }
        }
        return uniquePersons;
    }
}
