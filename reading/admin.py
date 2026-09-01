from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .forms import BookForm
from .models import Book, Language, Tag


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    form = BookForm
    list_display = (
        "cover_thumbnail",
        "title",
        "author",
        "language",
        "status",
        "started_at",
        "finished_at",
        "rating",
    )
    list_filter = ("status", "language", "rating")
    search_fields = ("title", "author", "notes", "tags__name", "language__name")
    ordering = ("status", "title")
    autocomplete_fields = ("language", "tags")

    @admin.display(description="Cover")
    def cover_thumbnail(self, obj):
        if not obj.cover_image:
            return "—"
        return format_html(
            (
                '<img src="{}" alt="Cover for {}" '
                'style="width: 36px; height: 54px; object-fit: cover; border-radius: 4px;" />'
            ),
            obj.cover_image.url,
            obj.title,
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "book_count", "is_used")
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


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "book_count")
    search_fields = ("name",)
    ordering = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(books_total=Count("books", distinct=True))

    @admin.display(description="Books", ordering="books_total")
    def book_count(self, obj):
        return obj.books_total
