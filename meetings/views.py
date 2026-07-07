from django.db.models import Q
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Meeting
from .serializers import MeetingSerializer


class MeetingListCreateView(generics.ListCreateAPIView):
    """
    GET  -> list every meeting where I'm the organizer OR the participant
    POST -> schedule a new meeting (I become the organizer)
    """
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Meeting.objects.filter(
            Q(organizer=user) | Q(participant=user)
        ).order_by('start_time')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class MeetingDetailView(generics.RetrieveDestroyAPIView):
    """GET one meeting, or DELETE (organizer only) to remove it entirely."""
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Meeting.objects.filter(Q(organizer=user) | Q(participant=user))

    def perform_destroy(self, instance):
        if instance.organizer != self.request.user:
            raise PermissionError('Only the organizer can delete this meeting.')
        instance.delete()


class MeetingActionView(APIView):
    """
    POST /api/meetings/<id>/<action>/
    action is one of: accept, reject, cancel
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        meeting = get_object_or_404(
            Meeting.objects.filter(Q(organizer=request.user) | Q(participant=request.user)),
            pk=pk
        )

        if action == 'accept':
            if meeting.participant != request.user:
                return Response({'detail': 'Only the invited participant can accept.'}, status=403)
            if meeting.status != 'pending':
                return Response({'detail': f'Meeting is already {meeting.status}.'}, status=400)

            # Re-check conflicts at accept-time too, in case something else got booked meanwhile
            conflict = Meeting.objects.filter(
                Q(organizer__in=[meeting.organizer, meeting.participant]) |
                Q(participant__in=[meeting.organizer, meeting.participant]),
                status='accepted',
                start_time__lt=meeting.end_time,
                end_time__gt=meeting.start_time,
            ).exclude(pk=meeting.pk)
            if conflict.exists():
                return Response({'detail': 'This slot was just booked elsewhere.'}, status=409)

            meeting.status = 'accepted'
            meeting.save()

        elif action == 'reject':
            if meeting.participant != request.user:
                return Response({'detail': 'Only the invited participant can reject.'}, status=403)
            meeting.status = 'rejected'
            meeting.save()

        elif action == 'cancel':
            if request.user not in (meeting.organizer, meeting.participant):
                return Response({'detail': 'Not allowed.'}, status=403)
            meeting.status = 'cancelled'
            meeting.save()

        else:
            return Response({'detail': 'Unknown action.'}, status=400)

        return Response(MeetingSerializer(meeting, context={'request': request}).data)
