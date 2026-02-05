from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Group, GroupInvitation, GroupMembership
from .serializers import GroupSerializer, GroupInvitationSerializer


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Group.objects.filter(members=self.request.user)

    @action(detail=True, methods=['post'], url_path='send-invitation')
    def send_invitation(self, request, pk=None):
        group = self.get_object()

        membership = GroupMembership.objects.filter(
            user=request.user, group=group
        ).first()

        if not membership or not membership.is_admin:
            return Response(
                {"detail": "Только администраторы группы могут приглашать"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = GroupInvitationSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        # Теперь просто save() — create() внутри сериализатора всё обработает
        invitation = serializer.save(
            group=group,
            inviter=request.user
        )

        return Response(
            GroupInvitationSerializer(invitation).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        group = self.get_object()
        if group.owner == request.user:
            return Response({"detail": "Владелец не может покинуть группу"}, status=400)
        GroupMembership.objects.filter(user=request.user, group=group).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupInvitationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupInvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GroupInvitation.objects.filter(
            invitee=self.request.user,
            status='pending'
        ).select_related('inviter', 'group')

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        invitation = self.get_object()
        invitation.status = 'accepted'
        invitation.save()

        GroupMembership.objects.get_or_create(
            user=request.user,
            group=invitation.group,
            defaults={'is_admin': False}
        )
        return Response({"status": "accepted"})

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        invitation = self.get_object()
        invitation.status = 'declined'
        invitation.save()
        return Response({"status": "declined"})