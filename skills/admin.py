from django.contrib import admin
from .models import Skill, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'level', 'rating', 'created_at')
    list_filter = ('category', 'level')
    search_fields = ('title', 'description', 'user__username')
