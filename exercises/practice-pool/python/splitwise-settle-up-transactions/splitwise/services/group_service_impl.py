from abc import ABC, abstractmethod
from typing import List
from splitwise.models import GroupMember, User, GroupAdmin, Group
from .group_service import GroupService
from splitwise.exceptions import NotFoundError
from splitwise.exceptions import UnAuthorizedAccessError
from splitwise.exceptions import InvalidUserError

class GroupServiceImpl(GroupService):

    def add_member(
            self,
            admin_id: int,
            group_id: int,
            user_id: int
    ) -> GroupMember:
        existing_member = GroupMember.objects.filter(
            group_id=group_id,
            user_id=user_id
        )

        if existing_member:
            return existing_member

        group = Group.objects.get(pk=group_id)

        group_admin: GroupAdmin = GroupAdmin.objects.filter(
            group=group,
            user_id=admin_id
        ).first()

        if not group_admin:
            raise UnAuthorizedAccessError("Unauthorized access")

        user: User = User.objects.get(pk=user_id)

        if not user:
            raise NotFoundError("User not found")

        return GroupMember.objects.create(
            group=group,
            user=user,
            added_by=group_admin.user
        )

    def remove_member(
            self,
            admin_id: int,
            group_id: int,
            user_id: int
    ) -> None:
        group = Group.objects.get(pk=group_id)
        admin = GroupAdmin.objects.filter(
            group_id=group_id,
            user_id=admin_id
        ).first()

        if not admin:
            raise UnAuthorizedAccessError("Unauthorized")

        user = User.objects.get(pk=user_id)

        group_member = GroupMember.objects.filter(
            group=group,
            user=user
        )

        if not group_member:
            raise NotFoundError("User not found")

        group_member.delete()

    def get_members(
            self,
            admin_id: int,
            group_id: int,
    ) -> List[User]:

        group = Group.objects.get(pk=group_id)

        admin = GroupAdmin.objects.filter(
            group=group,
            user_id=admin_id
        ).first()

        if not admin:
            raise UnAuthorizedAccessError("Unauthorized")

        group_members = GroupMember.objects.filter(
            group=group
        )

        return [group_member.user for group_member in group_members]
