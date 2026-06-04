from django import forms

from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "status", "started_at", "finished_at", "rating", "notes"]
        widgets = {
            "started_at": forms.DateInput(attrs={"type": "date"}),
            "finished_at": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 5}),
        }
