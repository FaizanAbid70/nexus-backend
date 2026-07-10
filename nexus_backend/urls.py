from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve as static_serve
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/meetings/', include('meetings.urls')),
    path('api/documents/', include('documents.urls')),
]

urlpatterns += [
    path('media/<path:path>', static_serve, {'document_root': settings.MEDIA_ROOT}),
]