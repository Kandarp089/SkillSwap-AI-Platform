from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.control_center_login, name='login'),
    path('logout/', views.control_center_logout, name='logout'),
    path('users/', views.user_list, name='users'),
    path('skills/', views.skill_list, name='skills'),
    path('categories/', views.category_list, name='categories'),
    path('ai-matches/', views.ai_matches_analytics, name='ai_matches'),
    path('exchanges/', views.exchange_list, name='exchanges'),
    path('certificates/', views.certificate_list, name='certificates'),
    path('support/', views.support_tickets, name='support'),
    path('reports/', views.reports_list, name='reports'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('health/', views.system_health, name='system_health'),
]
