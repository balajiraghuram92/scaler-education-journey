import unittest
from services import WaitListServiceImpl
from repositories import UserRepository, InMemoryUserRepositoryImpl
from repositories import WaitListPositionRepository, InMemoryWaitListPositionRepositoryImpl
from models import User, WaitListPosition, UserType


class TestWaitListService(unittest.TestCase):

    def setUp(self):
        self.user_repository = InMemoryUserRepositoryImpl()
        self.wait_list_position_repository = InMemoryWaitListPositionRepositoryImpl()
        self.wait_list_service = WaitListServiceImpl(
            user_repository=self.user_repository,
            wait_list_position_repository=self.wait_list_position_repository
        )
        self.init_data()

    def test_add_to_wait_list(self):

        users = self.data["users"]
        user = users[0]
        position = self.wait_list_service.add_user_to_wait_list(user.id)
        self.assertEqual(position, 1)

        user = users[1]
        position = self.wait_list_service.add_user_to_wait_list(user.id)
        self.assertEqual(position, 2)

    def test_process_from_wait_list(self):
        user1 = self.data["users"][0]
        user2 = self.data["users"][1]
        user3 = self.data["users"][2]

        for user in self.data["users"]:
            self.user_repository.save(user)
            wait_list_position = WaitListPosition(
                user=user
            )
            self.wait_list_position_repository.save(wait_list_position)

        admin = self.data["admin"]
        self.user_repository.save(admin)

        users = self.wait_list_service.process_wait_list(
            admin_user_id=admin.id,
            spots_count=2
        )

        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].id, user1.id)
        self.assertEqual(users[1].id, user2.id)

    def test_add_to_wait_list_twice(self):
        user1 = self.data["users"][0]
        user2 = self.data["users"][1]
        user3 = self.data["users"][2]

        for user in self.data["users"]:
            self.user_repository.save(user)

        position = self.wait_list_service.add_user_to_wait_list(user1.id)
        self.assertEqual(position, 1)

        position = self.wait_list_service.add_user_to_wait_list(user1.id)
        self.assertEqual(position, 1)

        position = self.wait_list_service.add_user_to_wait_list(user2.id)
        self.assertEqual(position, 2)

        position = self.wait_list_service.add_user_to_wait_list(user1.id)
        self.assertEqual(position, 1)

        position = self.wait_list_service.add_user_to_wait_list(user3.id)
        self.assertEqual(position, 3)

    def test_get_position(self):
        user1 = self.data["users"][0]
        user2 = self.data["users"][1]
        user3 = self.data["users"][2]

        for user in self.data["users"]:
            self.user_repository.save(user)
            wait_list_position = WaitListPosition(
                user=user
            )
            self.wait_list_position_repository.save(wait_list_position)

        position = self.wait_list_service.get_wait_list_position(user1.id)
        self.assertEqual(position, 1)

        position = self.wait_list_service.get_wait_list_position(user3.id)
        self.assertEqual(position, 3)


    def init_data(self):
        user1 = User(
            id=1,
            name="user1",
            phone="1234567890"
        )
        user2 = User(
            id=2,
            name="user2",
            phone="1234567890"
        )
        user3 = User(
            id=3,
            name="user3",
            phone="1234567890"
        )

        admin_user = User(
            id=4,
            name="admin",
            phone="1234567890",
            user_type=UserType.ADMIN
        )
        user1 = self.user_repository.save(user1)
        user2 = self.user_repository.save(user2)
        user3 = self.user_repository.save(user3)

        self.data = {
            "users": [user1, user2, user3],
            "admin": admin_user,
        }




