from datetime import timedelta

from django.test import TestCase
from splitwise.models import User, GroupMember, GroupAdmin, Group
from splitwise.exceptions import NotFoundError

from splitwise.services import GroupServiceImpl


class TestGroupService(TestCase):

    def setUp(self):

        self.group_service = GroupServiceImpl()
        self.generate_data()

    def test_group_service_add_member(self):
        group = self.data["group"]
        admin = self.data["admin"]
        not_added_users = self.data["not_added_users"]
        existing_members_count = GroupMember.objects.filter(group=group).count()

        self.group_service.add_member(
            group_id=group.pk,
            admin_id=admin.pk,
            user_id=not_added_users[0].pk
        )

        new_members_count = GroupMember.objects.filter(group=group).count()

        assert existing_members_count + 1 == new_members_count

    def test_group_service_add_member_twice(self):
        group = self.data["group"]
        admin = self.data["admin"]
        not_added_users = self.data["not_added_users"]
        existing_members_count = GroupMember.objects.filter(group=group).count()

        for iteration in range(2):
            self.group_service.add_member(
                group_id=group.pk,
                admin_id=admin.pk,
                user_id=not_added_users[0].pk
            )

        new_members_count = GroupMember.objects.filter(group=group).count()

        assert existing_members_count + 1 == new_members_count, "Adding member twice should not increase count twice"

    def test_group_service_remove_member(self):
        group = self.data["group"]
        admin = self.data["admin"]
        existing_members = GroupMember.objects.filter(group=group)

        existing_user = existing_members[0].user
        existing_members_count = len(existing_members)

        self.group_service.remove_member(
            group_id=group.pk,
            admin_id=admin.pk,
            user_id=existing_user.pk
        )

        new_members_count = GroupMember.objects.filter(group=group).count()

        assert existing_members_count - 1 == new_members_count, "Removing member should decrease count"

    def test_group_service_remove_invalid_user(self):
        group = self.data["group"]
        admin = self.data["admin"]

        with self.assertRaises(Exception):
            self.group_service.remove_member(
                group_id=group.pk,
                admin_id=admin.pk,
                user_id=100
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

        user4 = User.objects.create(
            name="Test4",
            phone="1234567890"
        )

        group1 = Group.objects.create(
            name="Test1",
            description="Test group"
        )

        admin_group_user = GroupAdmin.objects.create(
            group=group1,
            user=user1,
            added_by=None
        )

        GroupMember.objects.create(
            group=group1,
            user=user1,
            added_by=admin_group_user.user
        )

        GroupMember.objects.create(
            group=group1,
            user=user2,
            added_by=admin_group_user.user
        )

        GroupMember.objects.create(
            group=group1,
            user=user3,
            added_by=admin_group_user.user
        )

        self.data = {
            "group": group1,
            "admin": admin_group_user.user,
            "added_users": [user1, user2, user3],
            "not_added_users": [user4]
        }
