from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Meeting

User = get_user_model()


class MeetingUserMiniSerializer(serializers.ModelSerializer):
    """Small nested representation of a user, used inside meeting responses."""
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'profile_picture']


class MeetingSerializer(serializers.ModelSerializer):
    organizer = MeetingUserMiniSerializer(read_only=True)
    participant_detail = MeetingUserMiniSerializer(source='participant', read_only=True)
    participant = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )

    class Meta:
        model = Meeting
        fields = [
            'id', 'organizer', 'participant', 'participant_detail',
            'title', 'description', 'start_time', 'end_time',
            'status', 'room_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'room_name', 'created_at', 'updated_at']

    def validate(self, data):
        start = data.get('start_time')
        end = data.get('end_time')

        if start and end and start >= end:
            raise serializers.ValidationError('end_time must be after start_time.')

        request = self.context['request']
        organizer = request.user
        participant = data.get('participant')

        if participant and participant.id == organizer.id:
            raise serializers.ValidationError('You cannot schedule a meeting with yourself.')

        # Conflict detection: block if either person already has a
        # pending/accepted meeting that overlaps this time range.
        if start and end and participant:
            overlapping = Meeting.objects.filter(
                Q(organizer__in=[organizer, participant]) | Q(participant__in=[organizer, participant]),
                status__in=['pending', 'accepted'],
                start_time__lt=end,
                end_time__gt=start,
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError(
                    'This time slot conflicts with an existing meeting for you or the participant.'
                )

        return data

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)
