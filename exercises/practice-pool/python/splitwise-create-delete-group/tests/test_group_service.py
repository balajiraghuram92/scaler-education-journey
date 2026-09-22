from datetime import timedelta

from django.test import TestCase
from splitwise.models import User, GroupMember, GroupAdmin, Group
from splitwise.exceptions import NotFoundError

from splitwise.services import GroupServiceImpl


class TestGroupService(TestCase):

    def setUp(self):

        self.group_service = GroupServiceImpl()
        self.generate_data()

    def test_create_group(self):
        user = self.data["users"][0]

        group = self.group_service.create_group(
            user_id=user.pk,
            group_name="Test Group",
            group_description="Test Group Description"
        )

        assert group.name == "Test Group"
        assert group.description == "Test Group Description"
        assert group.pk is not None

    def test_delete_group(self):
        user = self.data["users"][0]

        group = Group.objects.create(
            name="Test Group",
            description="Test Group"
        )

        GroupMember.objects.create(
            group_id=group.pk,
            user_id=user.pk
        )

        GroupAdmin.objects.create(
            group_id=group.pk,
            user_id=user.pk
        )

        self.group_service.delete_group(
            group_id=group,
            admin_id=user.pk
        )

        with self.assertRaises(Exception):
            Group.objects.get(pk=group.pk)

    def test_delete_invalid_group(self):
        user = self.data["users"][0]
        with self.assertRaises(Exception):
            self.group_service.delete_group(
                group_id=100,
                admin_id=user.pk
            )

    def test_delete_group_invalid_user(self):
        user = self.data["users"][0]

        group = Group.objects.create(
            name="Test Group",
            description="Test Group"
        )

        GroupMember.objects.create(
            group_id=group.pk,
            user_id=user.pk
        )

        GroupAdmin.objects.create(
            group_id=group.pk,
            user_id=user.pk
        )

        with self.assertRaises(Exception):
                self.group_service.delete_group(
                    group_id=group.pk,
                    admin_id=100
                )

    def generate_data(self):
        # 4 users
        # group1 has 3 members
        # user4 is not in any group yet

        user1 = User.objects.create(
            name="Test1",
            phone="1234567890"
        )

        user2 = User.objects.create(
            name="Test2",
            phone="1234567890"
        )

        user3 = User.objects.create(
            name="Test3",
            phone="1234567890"
        )

        self.data = {
            "users": [user1, user2, user3],
        }
