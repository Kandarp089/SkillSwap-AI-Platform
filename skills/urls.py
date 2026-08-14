from django.urls import path
from . import views

app_name = "skills"

urlpatterns = [
    path('', views.browse_skills, name='browse_skills'),
    path('create/', views.create_skill, name='create_skill'),
    path('detail/', views.skill_detail, name='skill_detail'),
    path('detail/<int:pk>/', views.skill_detail, name='skill_detail_pk'),
    path('match/', views.ai_match, name='ai_match'),
    path('ai-match/', views.ai_match, name='ai-match'),
]