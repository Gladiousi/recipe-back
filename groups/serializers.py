# groups/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model  # ← этот импорт решает проблему
from django.shortcuts import get_object_or_404
from .models import Group, GroupMembership, GroupInvitation
from users.serializers import UserSerializer  # предполагается, что он существует


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
        GroupMembership.objects.create(user=user, group=group, is_admin=True)
        return group


class GroupInvitationSerializer(serializers.ModelSerializer):
    inviter = UserSerializer(read_only=True)
    invitee = UserSerializer(read_only=True)
    invitee_username = serializers.CharField(write_only=True, required=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = GroupInvitation
        fields = [
            'id', 'group', 'group_name', 'inviter', 'invitee',
            'invitee_username', 'status', 'created_at'
        ]
        read_only_fields = [
            'id', 'group', 'group_name', 'inviter', 'invitee',
            'status', 'created_at'
        ]

    def create(self, validated_data):
        """
        Здесь мы вручную обрабатываем создание приглашения,
        потому что invitee_username — это не поле модели
        """
        invitee_username = validated_data.pop('invitee_username')
        group = validated_data.pop('group')     # пришло из view
        inviter = validated_data.pop('inviter') # пришло из view

        User = get_user_model()

        try:
            invitee = User.objects.get(username=invitee_username)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "invitee_username": "Пользователь с таким именем не найден"
            })

        # Проверки на дубликаты (очень рекомендуется)
        if GroupMembership.objects.filter(group=group, user=invitee).exists():
            raise serializers.ValidationError({
                "invitee_username": "Пользователь уже состоит в группе"
            })

        if GroupInvitation.objects.filter(
            group=group,
            invitee=invitee,
            status='pending'
        ).exists():
            raise serializers.ValidationError({
                "invitee_username": "Приглашение этому пользователю уже отправлено и ожидает ответа"
            })

        # Создаём приглашение
        invitation = GroupInvitation.objects.create(
            group=group,
            inviter=inviter,
            invitee=invitee,
            # status по умолчанию 'pending'
        )

        return invitation