package com.assignment.adapters;

import com.assignment.models.SocialMediaPost;

import java.util.List;

public interface SocialMediaAdapter {

    List<SocialMediaPost> getPosts(Long userId, Long timestamp);

    void post(Long userId, String message);
}
