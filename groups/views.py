from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Group, GroupInvitation, GroupMembership
from .serializers import GroupSerializer, GroupInvitationSerializer
from django.shortcuts import get_object_or_404

class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Только группы, где пользователь является членом"""
        return Group.objects.filter(members=self.request.user)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Покинуть группу"""
        group = self.get_object()
        if group.owner == request.user:
            return Response(
                {"error": "Владелец не может покинуть группу"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        GroupMembership.objects.filter(user=request.user, group=group).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        """Удалить участника из группы (только для владельца)"""
        group = self.get_object()
        if group.owner != request.user:
            return Response(
                {"error": "Только владелец может удалять участников"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {"error": "user_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        GroupMembership.objects.filter(user_id=user_id, group=group).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupInvitationViewSet(viewsets.ModelViewSet):
    serializer_class = GroupInvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Приглашения для текущего пользователя"""
        return GroupInvitation.objects.filter(invitee=self.request.user, status='pending')

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Принять приглашение"""
        invitation = self.get_object()
        invitation.status = 'accepted'
        invitation.save()
        
        # Добавляем пользователя в группу
        GroupMembership.objects.create(user=request.user, group=invitation.group)
        
        return Response({"status": "accepted"})

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Отклонить приглашение"""
        invitation = self.get_object()
        invitation.status = 'declined'
        invitation.save()
        
        return Response({"status": "declined"})
