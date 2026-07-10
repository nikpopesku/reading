from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count

from .models import Book, Tag


class TagUsageFilter(SimpleListFilter):
    title = "usage"
    parameter_name = "usage"

    def lookups(self, request, model_admin):
        return (("used", "Used"), ("unused", "Unused"))

    def queryset(self, request, queryset):
        if self.value() == "used":
            return queryset.filter(books_total__gt=0)
        if self.value() == "unused":
            return queryset.filter(books_total=0)
        return queryset


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "started_at", "finished_at", "rating")
    list_filter = ("status", "rating")
    search_fields = ("title", "author", "notes", "tags__name")
    ordering = ("status", "title")
    autocomplete_fields = ("tags",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "book_count", "is_used")
    list_filter = (TagUsageFilter,)
    search_fields = ("name",)
    ordering = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(books_total=Count("books", distinct=True))

    @admin.display(description="Books", ordering="books_total")
    def book_count(self, obj):
        return obj.books_total

    @admin.display(boolean=True, description="Used")
    def is_used(self, obj):
        return obj.books_total > 0
