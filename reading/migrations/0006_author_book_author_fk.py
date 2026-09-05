from django.db import migrations, models
from django.db.models import deletion


def populate_authors(apps, schema_editor):
    Author = apps.get_model("books", "Author")
    Book = apps.get_model("books", "Book")

    for book in Book.objects.exclude(author_text=""):
        author_name = book.author_text.strip()
        if not author_name:
            continue
        author, _ = Author.objects.get_or_create(name=author_name)
        book.author = author
        book.save(update_fields=["author"])


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0005_language_book_language"),
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.RenameField(
            model_name="book",
            old_name="author",
            new_name="author_text",
        ),
        migrations.AddField(
            model_name="book",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=deletion.SET_NULL,
                related_name="books",
                to="books.author",
            ),
        ),
        migrations.RunPython(populate_authors, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="book",
            name="author_text",
        ),
    ]
