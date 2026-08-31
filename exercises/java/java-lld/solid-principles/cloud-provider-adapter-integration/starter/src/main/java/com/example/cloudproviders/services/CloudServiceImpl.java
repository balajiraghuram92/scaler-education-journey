package com.example.cloudproviders.services;

import com.example.cloudproviders.adapters.CloudAdapter;
import com.example.cloudproviders.exceptions.UserNotFoundException;
import com.example.cloudproviders.models.Connection;
import com.example.cloudproviders.models.User;
import com.example.cloudproviders.repositories.UserRepository;

// TODO: implement CloudService — look the user up via userRepository.findUserById(...),
// throwing UserNotFoundException("User not found") if absent, otherwise delegate the
// actual connection creation to cloudAdapter.createConnection(userId). This is what
// makes it trivial to swap cloud providers: only the CloudAdapter implementation changes.
public class CloudServiceImpl implements CloudService {
    private UserRepository userRepository;
    private CloudAdapter cloudAdapter;
    public CloudServiceImpl(UserRepository userRepository, CloudAdapter cloudAdapter) {
        this.userRepository = userRepository;
        this.cloudAdapter = cloudAdapter;
    }
    @Override
    public Connection createConnection(Long userId) throws UserNotFoundException {
        return null;
    }
}
