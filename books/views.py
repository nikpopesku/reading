from django.db.models import Count
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from .models import ACTIVE_BOOK_STATUSES, Book, BookStatus


def book_list(request):
    selected_status = request.GET.get("status", "")
    books = Book.objects.exclude(status=BookStatus.DELETED)
    if selected_status:
        if selected_status not in [status.value for status in ACTIVE_BOOK_STATUSES]:
            return HttpResponseBadRequest("Unknown status")
        books = books.filter(status=selected_status)

    counts_by_status = {
        row["status"]: row["total"] for row in books.values("status").annotate(total=Count("id"))
    }
    counts = {
        status.value: counts_by_status.get(status.value, 0) for status in ACTIVE_BOOK_STATUSES
    }

    return render(
        request,
        "books/book_list.html",
        {
            "books": books,
            "statuses": ACTIVE_BOOK_STATUSES,
            "selected_status": selected_status,
            "counts": counts,
            "total_count": books.count(),
        },
    )
