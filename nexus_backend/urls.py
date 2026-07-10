from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve as static_serve
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/meetings/', include('meetings.urls')),
    path('api/documents/', include('documents.urls')),
]

media_serve = xframe_options_exempt(static_serve)

urlpatterns += [
    path('media/<path:path>', media_serve, {'document_root': settings.MEDIA_ROOT}),
]