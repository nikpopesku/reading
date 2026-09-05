from django.core.management.base import BaseCommand

from reading.models import Author, Book


class Command(BaseCommand):
    help = "Populate the author list from existing book author values."

    def handle(self, *args, **options):
        created = 0
        linked = 0

        for book in Book.objects.exclude(author__isnull=True).select_related("author"):
            author_name = book.author.name.strip()
            if author_name == book.author.name:
                continue
            author, was_created = Author.objects.get_or_create(name=author_name)
            if was_created:
                created += 1
            if book.author_id != author.id:
                book.author = author
                book.save(update_fields=["author"])
                linked += 1

        self.stdout.write(
            self.style.SUCCESS(f"Authors populated: {created} created, {linked} books updated.")
        )
