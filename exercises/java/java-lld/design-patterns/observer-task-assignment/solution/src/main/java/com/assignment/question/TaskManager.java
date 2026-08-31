package com.assignment.question;

public class TaskManager extends Publisher {

    public void assignTask(Long taskId, Long userId) {
        notifyObservers(taskId, userId);
    }
}
