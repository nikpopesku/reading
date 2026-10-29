from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import AuthorForm
from .models import Author, Book


class AuthorFormTests(TestCase):
    def test_normalizes_unicode_and_whitespace(self):
        form = AuthorForm(data={"name": "  Jose\u0301   Example  "})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().name, "José Example")

    def test_equivalent_names_cannot_be_overridden(self):
        Author.objects.create(name="Nigel Poulton")
        for name in ["Nigel Poulton", "nigel poulton", " Nigel   Poulton "]:
            with self.subTest(name=name):
                form = AuthorForm(data={"name": name, "confirm_similar_name": "on"})
                self.assertFalse(form.is_valid())
                self.assertIn("already exists", str(form.errors["name"]))

    def test_canonical_unicode_duplicates_are_rejected(self):
        Author.objects.create(name="José Example")
        form = AuthorForm(data={"name": "Jose\u0301 Example"})
        self.assertFalse(form.is_valid())

    def test_existing_whitespace_variants_are_detected(self):
        Author.objects.create(name=" Nigel   Poulton ")
        form = AuthorForm(data={"name": "Nigel Poulton"})
        self.assertFalse(form.is_valid())

    def test_unchanged_author_is_not_its_own_match(self):
        author = Author.objects.create(name="Nigel Poulton")
        form = AuthorForm(instance=author, data={"name": author.name})
        self.assertTrue(form.is_valid(), form.errors)

    def test_unrelated_author_is_allowed(self):
        Author.objects.create(name="Nigel Poulton")
        form = AuthorForm(data={"name": "Carlo Collodi"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_similar_names_require_confirmation(self):
        for existing, proposed in [
            ("Nigel Poulton", "Nigel Poultron"),
            ("Братья Стругацкие", "Браться Стругацкие"),
        ]:
            with self.subTest(proposed=proposed):
                Author.objects.create(name=existing)
                form = AuthorForm(data={"name": proposed})
                self.assertFalse(form.is_valid())
                self.assertIn(existing, str(form.errors["name"]))
                confirmed = AuthorForm(data={"name": proposed, "confirm_similar_name": "on"})
                self.assertTrue(confirmed.is_valid(), confirmed.errors)

    def test_similar_rename_requires_confirmation(self):
        Author.objects.create(name="Nigel Poulton")
        author = Author.objects.create(name="Temporary Name")
        form = AuthorForm(instance=author, data={"name": "Nigel Poultron"})
        self.assertFalse(form.is_valid())

    def test_empty_name_is_rejected(self):
        form = AuthorForm(data={"name": "  "})
        self.assertFalse(form.is_valid())

    def test_distinct_accents_are_preserved_when_confirmed(self):
        Author.objects.create(name="Jose Example")
        form = AuthorForm(data={"name": "José Example", "confirm_similar_name": "on"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().name, "José Example")


class AuthorAdminPreventionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="author-review-test",
            email="author-test@example.invalid",
            password="test-only-password",
        )
        self.client.force_login(self.user)

    def test_book_author_uses_autocomplete(self):
        response = self.client.get(reverse("admin:books_book_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-field-name="author"')

    def test_admin_requires_explicit_confirmation(self):
        Author.objects.create(name="Nigel Poulton")
        url = reverse("admin:books_author_add")
        response = self.client.post(url, {"name": "Nigel Poultron", "_save": "Save"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nigel Poulton")
        self.assertFalse(Author.objects.filter(name="Nigel Poultron").exists())
        response = self.client.post(
            url,
            {
                "name": "Nigel Poultron",
                "confirm_similar_name": "on",
                "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Author.objects.filter(name="Nigel Poultron").exists())

    def test_admin_cannot_override_equivalent_name(self):
        Author.objects.create(name="Nigel Poulton")
        response = self.client.post(
            reverse("admin:books_author_add"),
            {
                "name": "nigel poulton",
                "confirm_similar_name": "on",
                "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Author.objects.count(), 1)

    def test_book_edit_preserves_author(self):
        author = Author.objects.create(name="Nigel Poulton")
        book = Book.objects.create(title="Docker Deep Dive", author=author)
        response = self.client.post(
            reverse("admin:books_book_change", args=[book.pk]),
            {
                "title": book.title,
                "author": author.pk,
                "status": book.status,
                "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 302)
        book.refresh_from_db()
        self.assertEqual(book.author_id, author.pk)

    def test_add_popup_displays_confirmation(self):
        response = self.client.get(reverse("admin:books_author_add"), {"_popup": "1"})
        self.assertContains(response, 'name="confirm_similar_name"')
        self.assertContains(response, 'name="_popup"')

    def test_nonstaff_cannot_create_authors(self):
        self.client.logout()
        response = self.client.post(
            reverse("admin:books_author_add"), {"name": "Unauthorized Author"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Author.objects.exists())
