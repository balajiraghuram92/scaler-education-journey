package com.assignment.adapters;

import com.assignment.api.TwitterApi;
import com.assignment.api.TwitterTweet;
import com.assignment.models.SocialMediaPost;

import java.util.List;

public class TwitterAdapter implements SocialMediaAdapter {
    private TwitterApi twitterApi = new TwitterApi();

    @Override
    public List<SocialMediaPost> getPosts(Long userId, Long timestamp) {
        // TODO: fetch tweets from twitterApi and map each TwitterTweet into a
        // common SocialMediaPost (id, tweet->text, userId, no timestamp available)
        return null;
    }

    @Override
    public void post(Long userId, String message) {
        // TODO: delegate to twitterApi.tweet(...)
    }
}
