from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings_page, name='settings'),
    path('achievements/', views.achievements, name='achievements'),
    path('certificates/', views.certificates, name='certificates'),
    path('community/', views.community, name='community'),
    path('events/', views.events, name='events'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('help-center/', views.help_center, name='help_center'),
    path('blog/', views.blog, name='blog'),
    path('careers/', views.careers, name='careers'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-use/', views.terms_of_use, name='terms_of_use'),
    path('cookies-policy/', views.cookies_policy, name='cookies_policy'),
    path('accessibility/', views.accessibility, name='accessibility'),
]