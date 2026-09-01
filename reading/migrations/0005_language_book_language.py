from django.db import migrations, models
from django.db.models import deletion


def create_default_languages(apps, schema_editor):
    Language = apps.get_model("books", "Language")
    for name in ("Italian", "Romanian", "Russian"):
        Language.objects.get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0004_book_cover_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="Language",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="book",
            name="language",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=deletion.SET_NULL,
                related_name="books",
                to="books.language",
            ),
        ),
        migrations.RunPython(create_default_languages, migrations.RunPython.noop),
    ]
