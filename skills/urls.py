from django.urls import path
from . import views

urlpatterns = [
    path('', views.browse_skills, name='browse_skills'),
    path('detail/', views.skill_detail, name='skill_detail'),
    path('ai-match/', views.ai_match, name='ai-match'),
]