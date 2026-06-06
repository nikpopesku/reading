from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Book, BookStatus


class BookModelTests(TestCase):
    def test_book_defaults_to_will_read(self):
        book = Book.objects.create(title="Dune", author="Frank Herbert")

        self.assertEqual(book.status, BookStatus.WILL_READ)
        self.assertEqual(str(book), "Dune by Frank Herbert")

    def test_book_without_author_uses_title_for_string(self):
        book = Book.objects.create(title="Sapiens")

        self.assertEqual(str(book), "Sapiens")


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

    def test_user_can_filter_books_without_login(self):
        Book.objects.create(title="Reading now", status=BookStatus.READING)
        Book.objects.create(title="Later", status=BookStatus.WILL_READ)

        response = self.client.get(reverse("book-list"), {"status": BookStatus.READING})

        self.assertContains(response, "Reading now")
        self.assertNotContains(response, "Later")

    def test_deleted_books_are_hidden_from_library(self):
        Book.objects.create(title="Visible", status=BookStatus.READING)
        Book.objects.create(title="Hidden", status=BookStatus.DELETED)

        response = self.client.get(reverse("book-list"))

        self.assertContains(response, "Visible")
        self.assertNotContains(response, "Hidden")

    def test_admin_login_is_available(self):
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])
