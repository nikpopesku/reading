# Generated manually for the initial Reading schema.

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(blank=True, max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("will_read", "Will read"),
                            ("reading", "Reading"),
                            ("read", "Read"),
                            ("deleted", "Deleted"),
                        ],
                        db_index=True,
                        default="will_read",
                        max_length=20,
                    ),
                ),
                ("started_at", models.DateField(blank=True, null=True)),
                ("finished_at", models.DateField(blank=True, null=True)),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["status", "title"]},
        ),
        migrations.AddConstraint(
            model_name="book",
            constraint=models.CheckConstraint(
                condition=models.Q(("rating__gte", 1), ("rating__lte", 5))
                | models.Q(("rating__isnull", True)),
                name="book_rating_between_1_and_5",
            ),
        ),
    ]
