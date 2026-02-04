from rest_framework import serializers
from .models import Group, GroupMembership, GroupInvitation
from users.serializers import UserSerializer

class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GroupMembership
        fields = ['id', 'user', 'joined_at', 'is_admin']


class GroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members_detail = GroupMembershipSerializer(source='groupmembership_set', many=True, read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'owner', 'members_detail', 'members_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_members_count(self, obj):
        return obj.members.count()

    def create(self, validated_data):
        user = self.context['request'].user
        group = Group.objects.create(owner=user, **validated_data)
        # Добавляем создателя как члена группы и админа
        GroupMembership.objects.create(user=user, group=group, is_admin=True)
        return group


class GroupInvitationSerializer(serializers.ModelSerializer):
    inviter = UserSerializer(read_only=True)
    invitee = UserSerializer(read_only=True)
    invitee_username = serializers.CharField(write_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = GroupInvitation
        fields = ['id', 'group', 'group_name', 'inviter', 'invitee', 'invitee_username', 'status', 'created_at']
        read_only_fields = ['id', 'inviter', 'invitee', 'status', 'created_at']

    def create(self, validated_data):
        invitee_username = validated_data.pop('invitee_username')
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            invitee = User.objects.get(username=invitee_username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"invitee_username": "Пользователь не найден"})

        group = validated_data['group']
        inviter = self.context['request'].user

        # Проверка, что пользователь уже не в группе
        if group.members.filter(id=invitee.id).exists():
            raise serializers.ValidationError({"invitee_username": "Пользователь уже в группе"})

        # Проверка на существующее приглашение
        if GroupInvitation.objects.filter(group=group, invitee=invitee, status='pending').exists():
            raise serializers.ValidationError({"invitee_username": "Приглашение уже отправлено"})

        invitation = GroupInvitation.objects.create(
            group=group,
            inviter=inviter,
            invitee=invitee
        )
        return invitation
