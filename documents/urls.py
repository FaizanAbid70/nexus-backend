from django.urls import path
from .views import DocumentListCreateView, DocumentDetailView, DocumentSignView

urlpatterns = [
    path('', DocumentListCreateView.as_view(), name='document-list-create'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('<int:pk>/sign/', DocumentSignView.as_view(), name='document-sign'),
]
