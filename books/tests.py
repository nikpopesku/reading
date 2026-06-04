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

    def test_anonymous_user_is_redirected(self):
        response = self.client.get(reverse("book-list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_authenticated_user_can_filter_books(self):
        self.client.force_login(self.user)
        Book.objects.create(title="Reading now", status=BookStatus.READING)
        Book.objects.create(title="Later", status=BookStatus.WILL_READ)

        response = self.client.get(reverse("book-list"), {"status": BookStatus.READING})

        self.assertContains(response, "Reading now")
        self.assertNotContains(response, "Later")

    def test_authenticated_user_can_create_book(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("book-create"),
            {
                "title": "The Left Hand of Darkness",
                "author": "Ursula K. Le Guin",
                "status": BookStatus.WILL_READ,
                "rating": "",
                "notes": "",
                "started_at": "",
                "finished_at": "",
            },
        )

        self.assertRedirects(response, reverse("book-list"))
        self.assertTrue(Book.objects.filter(title="The Left Hand of Darkness").exists())

    def test_htmx_status_update_marks_read_dates(self):
        self.client.force_login(self.user)
        book = Book.objects.create(title="Finished")

        response = self.client.post(
            reverse("book-status", args=[book.pk]), {"status": BookStatus.READ}
        )

        self.assertEqual(response.status_code, 200)
        book.refresh_from_db()
        self.assertEqual(book.status, BookStatus.READ)
        self.assertIsNotNone(book.started_at)
        self.assertIsNotNone(book.finished_at)
