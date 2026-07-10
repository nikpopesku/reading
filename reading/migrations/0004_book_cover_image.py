from django.core.validators import FileExtensionValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0003_merge_0002_rating_scale_to_10_0002_tag_book_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="cover_image",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="book-covers/",
                help_text="Upload a JPG or PNG cover up to 2 MB and 1200×1600 pixels.",
                validators=[FileExtensionValidator(["jpg", "jpeg", "png"])],
            ),
        ),
    ]
