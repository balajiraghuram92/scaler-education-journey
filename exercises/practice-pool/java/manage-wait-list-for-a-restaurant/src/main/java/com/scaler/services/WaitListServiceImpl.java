package com.scaler.services;

import com.scaler.exceptions.UnauthorizedAccessException;
import com.scaler.exceptions.UserNotFoundException;
import com.scaler.models.User;
import com.scaler.models.UserType;
import com.scaler.models.WaitListPosition;
import com.scaler.repositories.UserRepository;
import com.scaler.repositories.WaitListPositionRepository;

import java.util.Date;
import java.util.List;

public class WaitListServiceImpl implements WaitListService{

        private WaitListPositionRepository waitListPositionRepository;
        private UserRepository userRepository;

        public WaitListServiceImpl(WaitListPositionRepository waitListPositionRepository, UserRepository userRepository) {
                this.waitListPositionRepository = waitListPositionRepository;
                this.userRepository = userRepository;
        }


        @Override
        public int addUserToWaitList(long userId) throws UserNotFoundException {
                User user = userRepository.findById(userId).orElseThrow(() -> new UserNotFoundException("User not found"));
                List<WaitListPosition> all = waitListPositionRepository.findAll();
                for (int i = 0; i < all.size(); i++) {
                        if (all.get(i).getUser().getId() == user.getId()) {
                                return i + 1;
                        }
                }
                WaitListPosition waitListPosition = new WaitListPosition();
                waitListPosition.setUser(user);
                waitListPosition.setInsertedAt(new Date());
                waitListPositionRepository.save(waitListPosition);
                all = waitListPositionRepository.findAll();
                return all.size();
        }

        @Override
        public int getWaitListPosition(long userId) throws UserNotFoundException {
                User user = userRepository.findById(userId).orElseThrow(() -> new UserNotFoundException("User not found"));
                List<WaitListPosition> all = waitListPositionRepository.findAll();
                for (int i = 0; i < all.size(); i++) {
                        if (all.get(i).getUser().getId() == user.getId()) {
                                return i + 1;
                        }
                }
                return -1;
        }

        @Override
        public void updateWaitList(long adminUserId, int numberOfSpots) throws UserNotFoundException, UnauthorizedAccessException {
                User adminUser = userRepository.findById(adminUserId).orElseThrow(() -> new UserNotFoundException("User not found"));
                if(adminUser.getUserType() != UserType.ADMIN) {
                        throw new UnauthorizedAccessException("User not found");
                }
                List<WaitListPosition> all = waitListPositionRepository.findAll();
                numberOfSpots = Math.min(numberOfSpots, all.size());
                for (int i = 0; i < numberOfSpots; i++) {
                        waitListPositionRepository.delete(all.get(i));
                }
        }
}
