from django import forms

from .models import ACTIVE_BOOK_STATUSES, Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "language",
            "cover_image",
            "status",
            "started_at",
            "finished_at",
            "rating",
            "notes",
        ]
        widgets = {
            "cover_image": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png"}),
            "started_at": forms.DateInput(attrs={"type": "date"}),
            "finished_at": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            (status.value, status.label) for status in ACTIVE_BOOK_STATUSES
        ]
