from django.urls import path
from .views import ping, RegisterView, LoginView, MyProfileView, PublicProfileView, UserListView

urlpatterns = [
    path('ping/', ping, name='ping'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/me/', MyProfileView.as_view(), name='my-profile'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('profile/<int:user_id>/', PublicProfileView.as_view(), name='public-profile'),
]