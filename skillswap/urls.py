from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from certificates.views import verify_certificate

urlpatterns = [
    # Consolidated Single Super Admin Control Center (/admin/ redirects to /control-center/)
    path('admin/', RedirectView.as_view(url='/control-center/', permanent=False)),
    path('control-center/', include('adminpanel.urls')),
    path('verify/certificate/<str:certificate_id>/', verify_certificate, name='verify_certificate'),

    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('profile/', include('profiles.urls')),
    path('skills/', include('skills.urls')),
    path('chat/', include('chatapp.urls')),
    path('requests/', include('exchanges.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )