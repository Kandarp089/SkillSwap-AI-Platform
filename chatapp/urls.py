from django.urls import path
from . import views

app_name = "chatapp"

urlpatterns = [
    path('', views.chat_home, name='chat'),
    path('send/', views.send_message, name='send_message'),
]