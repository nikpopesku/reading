from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "started_at", "finished_at", "rating")
    list_filter = ("status", "rating")
    search_fields = ("title", "author", "notes")
    ordering = ("status", "title")
