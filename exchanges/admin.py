from django.contrib import admin
from .models import ExchangeRequest

@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'offered_skill', 'requested_skill', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'offered_skill', 'requested_skill')
