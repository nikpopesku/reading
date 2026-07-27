import struct
import tempfile
import zlib
from datetime import date
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import (
    MAX_BOOK_COVER_IMAGE_HEIGHT,
    MAX_BOOK_COVER_IMAGE_SIZE_BYTES,
    MAX_BOOK_COVER_IMAGE_WIDTH,
    Book,
    BookStatus,
    Tag,
)
from .views import DEFAULT_PAGE_SIZE


def make_png_bytes(*, width=48, height=72, color=(36, 93, 99)):
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(
        ">IIBBBBB",
        width,
        height,
        8,
        2,
        0,
        0,
        0,
    )
    ihdr_body = b"IHDR" + ihdr_data
    ihdr = (
        struct.pack(">I", len(ihdr_data))
        + ihdr_body
        + struct.pack(">I", zlib.crc32(ihdr_body) & 0xFFFFFFFF)
    )

    row = bytes([0]) + bytes(color) * width
    raw = row * height
    compressed = zlib.compress(raw)
    idat_body = b"IDAT" + compressed
    idat = (
        struct.pack(">I", len(compressed))
        + idat_body
        + struct.pack(">I", zlib.crc32(idat_body) & 0xFFFFFFFF)
    )

    iend_body = b"IEND"
    iend = struct.pack(">I", 0) + iend_body + struct.pack(">I", zlib.crc32(iend_body) & 0xFFFFFFFF)
    return signature + ihdr + idat + iend


def make_image_file(*, width=48, height=72, name="cover.png"):
    return SimpleUploadedFile(
        name, make_png_bytes(width=width, height=height), content_type="image/png"
    )


class BookModelTests(TestCase):
    def test_book_defaults_to_will_read(self):
        book = Book.objects.create(title="Dune", author="Frank Herbert")

        self.assertEqual(book.status, BookStatus.WILL_READ)
        self.assertEqual(str(book), "Dune by Frank Herbert")

    def test_book_without_author_uses_title_for_string(self):
        book = Book.objects.create(title="Sapiens")

        self.assertEqual(str(book), "Sapiens")

    def test_book_rating_uses_ten_point_scale(self):
        book = Book(title="Deep Work", rating=10)

        book.full_clean()

        with self.assertRaises(ValidationError):
            Book(title="Invalid", rating=11).full_clean()

    def test_book_can_have_tags(self):
        book = Book.objects.create(title="Dune")
        fiction = Tag.objects.create(name="fiction")
        classics = Tag.objects.create(name="classics")

        book.tags.add(fiction, classics)

        self.assertEqual(
            list(book.tags.order_by("name").values_list("name", flat=True)),
            ["classics", "fiction"],
        )

    def test_book_cover_image_can_be_uploaded_and_displayed_as_thumbnail(self):
        book = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            cover_image=make_image_file(),
        )

        response = self.client.get(reverse("book-list"))

        self.assertContains(response, book.cover_image.url)
        self.assertContains(response, 'class="book-cover-thumb"', html=False)

    def test_book_cover_media_file_is_served_when_debug_is_disabled(self):
        with tempfile.TemporaryDirectory() as media_root:
            cover_path = Path(media_root) / "book-covers" / "cover.png"
            cover_path.parent.mkdir(parents=True)
            cover_path.write_bytes(make_png_bytes())

            with override_settings(DEBUG=False, MEDIA_ROOT=media_root):
                response = self.client.get("/media/book-covers/cover.png")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "image/png")

    def test_book_cover_image_rejects_non_image_extensions(self):
        book = Book(title="Dune", cover_image=SimpleUploadedFile("cover.gif", b"gif data"))

        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_book_cover_image_rejects_images_that_are_too_large(self):
        image = make_image_file()
        oversized = SimpleUploadedFile(
            "cover.png",
            image.read() + b"0" * (MAX_BOOK_COVER_IMAGE_SIZE_BYTES + 1),
            content_type="image/png",
        )
        book = Book(title="Dune", cover_image=oversized)

        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_book_cover_image_rejects_images_with_large_dimensions(self):
        book = Book(
            title="Dune",
            cover_image=make_image_file(
                width=MAX_BOOK_COVER_IMAGE_WIDTH + 1,
                height=MAX_BOOK_COVER_IMAGE_HEIGHT + 1,
            ),
        )

        with self.assertRaises(ValidationError):
            book.full_clean()


class BookViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="admin", password="password")

    def test_homepage_is_public(self):
        response = self.client.get(reverse("book-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Library")

    def test_homepage_renders_books_table(self):
        Book.objects.create(title="Reading now", author="Author", status=BookStatus.READING)

        response = self.client.get(reverse("book-list"))

        self.assertContains(response, "<table", html=False)
        self.assertContains(response, "Reading now")
        self.assertContains(response, "Author")

    def test_homepage_paginates_books_by_default(self):
        for index in range(DEFAULT_PAGE_SIZE + 1):
            Book.objects.create(title=f"Book {index:02d}", author="Author")

        response = self.client.get(reverse("book-list"))

        self.assertEqual(response.context["page_obj"].paginator.per_page, DEFAULT_PAGE_SIZE)
        self.assertEqual(len(response.context["books"]), DEFAULT_PAGE_SIZE)
        self.assertEqual(response.context["total_count"], DEFAULT_PAGE_SIZE + 1)
        self.assertContains(response, "Books per page")
        self.assertContains(response, "Next")

    def test_user_can_change_page_size(self):
        for index in range(12):
            Book.objects.create(title=f"Book {index:02d}")

        response = self.client.get(reverse("book-list"), {"page_size": 10})

        self.assertEqual(response.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(len(response.context["books"]), 10)

    def test_homepage_displays_book_tags(self):
        book = Book.objects.create(title="Tagged", status=BookStatus.READING)
        fiction = Tag.objects.create(name="fiction")
        classics = Tag.objects.create(name="classics")
        book.tags.add(fiction, classics)

        response = self.client.get(reverse("book-list"))

        self.assertContains(response, "fiction")
        self.assertContains(response, "classics")

    def test_user_can_filter_books_without_login(self):
        Book.objects.create(title="Reading now", status=BookStatus.READING)
        Book.objects.create(title="Later", status=BookStatus.WILL_READ)

        response = self.client.get(reverse("book-list"), {"status": BookStatus.READING})

        self.assertContains(response, "Reading now")
        self.assertNotContains(response, "Later")

    def test_user_can_filter_and_paginate_books_together(self):
        for index in range(11):
            Book.objects.create(title=f"Reading {index:02d}", status=BookStatus.READING)
        Book.objects.create(title="Later", status=BookStatus.WILL_READ)

        response = self.client.get(
            reverse("book-list"),
            {"status": BookStatus.READING, "page_size": 10, "page": 2},
        )

        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(len(response.context["books"]), 1)
        self.assertEqual(
            list(response.context["books"].values_list("title", flat=True)),
            ["Reading 10"],
        )
        self.assertNotContains(response, "Later")

    def test_user_can_sort_books_by_status(self):
        Book.objects.create(title="Read", status=BookStatus.READ)
        Book.objects.create(title="Will read", status=BookStatus.WILL_READ)
        Book.objects.create(title="Reading", status=BookStatus.READING)

        response = self.client.get(reverse("book-list"), {"sort": "status"})

        self.assertEqual(
            list(response.context["books"].values_list("title", flat=True)),
            ["Will read", "Reading", "Read"],
        )

    def test_user_can_sort_books_by_title(self):
        Book.objects.create(title="Zulu", status=BookStatus.READ)
        Book.objects.create(title="Alpha", status=BookStatus.WILL_READ)
        Book.objects.create(title="Mike", status=BookStatus.READING)

        response = self.client.get(reverse("book-list"), {"sort": "title"})

        self.assertEqual(
            list(response.context["books"].values_list("title", flat=True)),
            ["Alpha", "Mike", "Zulu"],
        )

    def test_user_can_sort_books_by_author(self):
        Book.objects.create(title="Zulu", author="Zed")
        Book.objects.create(title="Alpha", author="Alice")
        Book.objects.create(title="Mike", author="Mike")

        response = self.client.get(reverse("book-list"), {"sort": "author"})

        self.assertEqual(
            list(response.context["books"].values_list("author", flat=True)),
            ["Alice", "Mike", "Zed"],
        )

    def test_user_can_sort_books_by_finished_date(self):
        Book.objects.create(title="Older", status=BookStatus.READ, finished_at=date(2024, 1, 1))
        Book.objects.create(title="Newer", status=BookStatus.READ, finished_at=date(2024, 2, 1))
        Book.objects.create(title="Unfinished", status=BookStatus.READ)

        response = self.client.get(reverse("book-list"), {"sort": "-finished_at"})

        self.assertEqual(
            list(response.context["books"].values_list("title", flat=True)),
            ["Newer", "Older", "Unfinished"],
        )

    def test_user_can_sort_books_by_started_date(self):
        Book.objects.create(title="Older", status=BookStatus.READING, started_at=date(2024, 1, 1))
        Book.objects.create(title="Newer", status=BookStatus.READING, started_at=date(2024, 2, 1))
        Book.objects.create(title="Unstarted", status=BookStatus.READING)

        response = self.client.get(reverse("book-list"), {"sort": "started_at"})

        self.assertEqual(
            list(response.context["books"].values_list("title", flat=True)),
            ["Older", "Newer", "Unstarted"],
        )

    def test_user_can_sort_books_by_rating(self):
        Book.objects.create(title="Low", status=BookStatus.READ, rating=2)
        Book.objects.create(title="High", status=BookStatus.READ, rating=9)
        Book.objects.create(title="Unrated", status=BookStatus.READ)

        response = self.client.get(reverse("book-list"), {"sort": "-rating"})

        self.assertEqual(
            list(response.context["books"].values_list("title", flat=True)),
            ["High", "Low", "Unrated"],
        )

    def test_deleted_books_are_hidden_from_library(self):
        Book.objects.create(title="Visible", status=BookStatus.READING)
        Book.objects.create(title="Hidden", status=BookStatus.DELETED)

        response = self.client.get(reverse("book-list"))

        self.assertContains(response, "Visible")
        self.assertNotContains(response, "Hidden")

    def test_admin_tag_changelist_shows_usage_counts(self):
        admin_user = get_user_model().objects.create_superuser(
            username="superadmin", password="password", email="admin@example.com"
        )
        self.client.force_login(admin_user)
        used_tag = Tag.objects.create(name="used")
        Tag.objects.create(name="unused")
        book = Book.objects.create(title="Tagged", status=BookStatus.READING)
        book.tags.add(used_tag)

        response = self.client.get(reverse("admin:books_tag_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "used")
        self.assertContains(response, "unused")
        self.assertContains(response, "1")
        self.assertContains(response, "0")

    def test_admin_login_is_available(self):
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])
