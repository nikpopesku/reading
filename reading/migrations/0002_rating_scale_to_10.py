from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="book",
            name="book_rating_between_1_and_5",
        ),
        migrations.AlterField(
            model_name="book",
            name="rating",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                help_text="Use a 1-10 scale",
                validators=[MinValueValidator(1), MaxValueValidator(10)],
            ),
        ),
        migrations.AddConstraint(
            model_name="book",
            constraint=models.CheckConstraint(
                condition=models.Q(("rating__gte", 1), ("rating__lte", 10))
                | models.Q(("rating__isnull", True)),
                name="book_rating_between_1_and_10",
            ),
        ),
    ]
