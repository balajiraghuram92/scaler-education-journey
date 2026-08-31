package com.assignment.adapters;

import com.assignment.api.FacebookApi;
import com.assignment.api.FacebookPost;
import com.assignment.models.SocialMediaPost;

import java.util.List;

public class FacebookAdapter implements SocialMediaAdapter {
    private FacebookApi facebookApi = new FacebookApi();

    @Override
    public List<SocialMediaPost> getPosts(Long userId, Long timestamp) {
        // TODO: fetch posts from facebookApi and map each FacebookPost into a
        // common SocialMediaPost (id, status->text, userId, timestamp)
        return null;
    }

    @Override
    public void post(Long userId, String message) {
        // TODO: delegate to facebookApi.postFacebookStatus(...)
    }
}
