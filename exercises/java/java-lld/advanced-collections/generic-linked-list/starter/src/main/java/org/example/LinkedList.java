package org.example;

class ListNode<T> {
    T data;
    ListNode<T> next;

    public ListNode(T data) {
        this.data = data;
        this.next = null;
    }
}

// TODO: implement a generic singly linked list —
//  - add(data): append a new node holding data to the end of the list.
//  - display(): print each element's data followed by a space, in list order.
//  - isEmpty(): true when the list has no nodes.
//  - size(): count of nodes currently in the list.
public class LinkedList<T> {
    private ListNode<T> head;

    public LinkedList() {
        this.head = null;
    }

    public void add(T data) {

    }

    public void display() {

    }

    public boolean isEmpty() {
        return false;
    }

    public int size() {
        return 0;
    }
}
