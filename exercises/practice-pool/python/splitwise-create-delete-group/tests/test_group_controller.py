from datetime import timedelta

from django.test import TestCase

from splitwise.controllers import GroupController
from splitwise.models import User, GroupMember, GroupAdmin, Group
from splitwise.dtos import CreateGroupResponseDto, CreateGroupRequestDto
from splitwise.dtos import DeleteGroupResponseDto, DeleteGroupRequestDto
from splitwise.dtos import ResponseStatus

from splitwise.services import GroupServiceImpl


class TestGroupController(TestCase):

    def setUp(self):

        self.group_service = GroupServiceImpl()
        self.group_controller = GroupController(self.group_service)
        self.generate_data()

    def test_create_group(self):
        user = self.data["users"][0]

        response = self.group_controller.create_group(
            CreateGroupRequestDto(
                user_id=user.pk,
                group_name="Test Group",
                group_description="Test Group Description"
            )
        )

        assert response.response_status == ResponseStatus.SUCCESS
        group = response.group
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

        response = self.group_controller.delete_group(
            DeleteGroupRequestDto(
                group_id=group,
                admin_id=user.pk
            )
        )

        assert response.response_status == ResponseStatus.SUCCESS
        assert Group.objects.filter(pk=group.pk).count() == 0

    def test_delete_invalid_group(self):
        user = self.data["users"][0]

        response = self.group_controller.delete_group(
            DeleteGroupRequestDto(
                group_id=100,
                admin_id=user.pk
            )
        )

        assert response.response_status == ResponseStatus.FAILURE


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

        response = self.group_controller.delete_group(
            DeleteGroupRequestDto(
                    group_id=group.pk,
                    admin_id=100
            )
        )

        assert response.response_status == ResponseStatus.FAILURE

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
