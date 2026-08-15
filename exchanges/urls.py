from django.urls import path
from . import views

app_name = "exchanges"

urlpatterns = [
    path('', views.requests_page, name='requests'),
    path('send/', views.send_request, name='send_request'),
    path('accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('complete/<int:request_id>/', views.complete_request, name='complete_request'),
    path('cancel/<int:request_id>/', views.cancel_request, name='cancel_request'),
    path('my-exchanges/', views.my_exchanges, name='my_exchanges'),
]