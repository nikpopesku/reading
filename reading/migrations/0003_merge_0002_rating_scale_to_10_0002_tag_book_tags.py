from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0002_rating_scale_to_10"),
        ("books", "0002_tag_book_tags"),
    ]

    operations = []
