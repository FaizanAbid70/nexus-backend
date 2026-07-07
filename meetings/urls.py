from django.urls import path
from .views import MeetingListCreateView, MeetingDetailView, MeetingActionView

urlpatterns = [
    path('', MeetingListCreateView.as_view(), name='meeting-list-create'),
    path('<int:pk>/', MeetingDetailView.as_view(), name='meeting-detail'),
    path('<int:pk>/<str:action>/', MeetingActionView.as_view(), name='meeting-action'),
]
