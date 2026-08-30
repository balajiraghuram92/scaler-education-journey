# Generic Singly Linked List Implementation

Source folder: `1773391574_2c32354d002745d7/Generic_Linked_L-solution`

## Problem Statement

Your task is to implement a generic singly linked list in Java, capable of storing data of any type. The class `ListNode` represents the nodes of the linked list and has been provided. You are required to complete the implementation of the `LinkedList` class, which should include methods for adding elements to the list, displaying the list contents, checking if the list is empty, and determining the size of the list.

### Instructions

1. Inside the `LinkedList` class, initialize the head node to null in the constructor. The head node will be used to keep track of the start of the list.
2. Implement the add method to `add` a new node with the specified data at the end of the list. This method should take the data to be added as a parameter and does not return anything.
3. Implement the `display` method to print the data of each node in the list, separated by spaces. Ensure that no additional spaces or newline characters are printed at the end of the output.
4. Implement the `isEmpty` method to return true if the list is empty (i.e., the head is null), otherwise false. This method does not take any parameters and returns a boolean value.
5. Implement the `size` method to return the number of nodes currently in the list. This method does not take any parameters and returns an integer value representing the size of the list.

## Graded Contract (from tests)

From `TestLinkedList.java`:

- Class `LinkedList<T>` must exist in package `org.example` with one type parameter
- Must have constructor `LinkedList()` with no parameters
- Must have method `void add(T data)` to add elements at the end
- Must have method `void display()` to print all elements separated by spaces (with trailing space, no newline)
- Must have method `boolean isEmpty()` returning true if list is empty
- Must have method `int size()` returning the number of elements in list
- Class `ListNode<T>` must exist as a helper class (package-private)
- `add()` must handle null values correctly
- `display()` on empty list must print nothing
- `isEmpty()` must return true for new list, false after adding element
- `size()` must return correct count after multiple additions

## Learner Template

```java
package org.example;

class ListNode<T> {
    T data;
    ListNode<T> next;

    public ListNode(T data) {
        this.data = data;
        this.next = null;
    }
}

public class LinkedList<T> {

    // Private head node to track start of list
    // TODO: Declare private ListNode<T> head

    public LinkedList() {
        // TODO: Initialize head to null
    }

    public void add(T data) {
        // TODO: Create new node with data
        // TODO: If head is null, set as head
        // TODO: Otherwise, traverse to end and append
    }

    public void display() {
        // TODO: Traverse from head and print each data followed by space
        // TODO: Do not print newline at the end
    }

    public boolean isEmpty() {
        // TODO: Return true if head is null
    }

    public int size() {
        // TODO: Traverse list and count nodes
        // TODO: Return count
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field declarations
- Traversal logic details
- Memory management considerations (no explicit delete needed in Java)
- Main method and example usage
- Edge case handling specifics
