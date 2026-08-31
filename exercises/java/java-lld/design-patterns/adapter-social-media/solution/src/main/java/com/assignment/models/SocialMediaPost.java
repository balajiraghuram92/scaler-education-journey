package com.assignment.models;

public class SocialMediaPost {
    private String id;
    private String text;
    private Long userId;
    private Long timestamp;

    public SocialMediaPost(String id, String text, Long userId, Long timestamp) {
        this.id = id;
        this.text = text;
        this.userId = userId;
        this.timestamp = timestamp;
    }
}
