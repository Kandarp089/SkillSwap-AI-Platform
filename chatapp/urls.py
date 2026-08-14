from django.urls import path
from . import views

app_name = "chatapp"

urlpatterns = [
    path('', views.chat_home, name='chat'),
]