from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class BookStatus(models.TextChoices):
    WILL_READ = "will_read", "Will read"
    READING = "reading", "Reading"
    READ = "read", "Read"


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=BookStatus.choices,
        default=BookStatus.WILL_READ,
        db_index=True,
    )
    started_at = models.DateField(blank=True, null=True)
    finished_at = models.DateField(blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "title"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5) | models.Q(rating__isnull=True),
                name="book_rating_between_1_and_5",
            )
        ]

    def __str__(self) -> str:
        if self.author:
            return f"{self.title} by {self.author}"
        return self.title
