from splitwise.models import GroupMember, User, GroupAdmin, Group
from .group_service import GroupService


class GroupServiceImpl(GroupService):
    def create_group(self, user_id: int, group_name: str, group_description: str) -> Group:
        user = User.objects.get(pk=user_id)

        group = Group.objects.create(name=group_name, description=group_description)

        GroupMember.objects.create(
            group=group,
            user=user
        )

        GroupAdmin.objects.create(
            group=group,
            user=user
        )

        return group

    def delete_group(self, admin_id: int, group_id: int):

        group_admin = GroupAdmin.objects.get(
            user_id=admin_id,
            group_id=group_id
        )

        group = group_admin.group
        group.delete()

