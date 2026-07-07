from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Document
from .serializers import DocumentSerializer, DocumentSignSerializer


class DocumentListCreateView(generics.ListCreateAPIView):
    """
    GET  -> documents I uploaded, OR documents attached to a meeting I'm part of
    POST -> upload a new document (multipart/form-data: title, file, meeting[optional])
    """
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        user = self.request.user
        return Document.objects.filter(
            Q(uploaded_by=user) |
            Q(meeting__organizer=user) |
            Q(meeting__participant=user)
        ).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Document.objects.filter(
            Q(uploaded_by=user) |
            Q(meeting__organizer=user) |
            Q(meeting__participant=user)
        ).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_destroy(self, instance):
        if instance.uploaded_by != self.request.user:
            raise PermissionError('Only the uploader can delete this document.')
        instance.delete()


class DocumentSignView(APIView):
    """POST a signature image -> attaches it to the document and marks it signed."""
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, pk):
        document = get_object_or_404(
            Document.objects.filter(
                Q(uploaded_by=request.user) |
                Q(meeting__organizer=request.user) |
                Q(meeting__participant=request.user)
            ),
            pk=pk
        )

        serializer = DocumentSignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        document.signature_image = serializer.validated_data['signature_image']
        document.signed_by = request.user
        document.signed_at = timezone.now()
        document.status = 'signed'
        document.save()

        return Response(DocumentSerializer(document, context={'request': request}).data)
