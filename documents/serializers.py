from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True)
    file_url = serializers.SerializerMethodField()
    signature_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file', 'file_url', 'version', 'status',
            'uploaded_by', 'uploaded_by_name', 'meeting',
            'signature_image', 'signature_url', 'signed_by', 'signed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'uploaded_by', 'version', 'status',
            'signature_image', 'signed_by', 'signed_at', 'created_at', 'updated_at'
        ]

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

    def get_signature_url(self, obj):
        request = self.context.get('request')
        if obj.signature_image and request:
            return request.build_absolute_uri(obj.signature_image.url)
        return None

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class DocumentSignSerializer(serializers.Serializer):
    signature_image = serializers.ImageField()
