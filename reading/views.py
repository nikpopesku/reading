from django.db.models import Count, Q
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from .models import ACTIVE_BOOK_STATUSES, Book, BookStatus


def book_list(request):
    selected_status = request.GET.get("status", "")
    selected_year = request.GET.get("year", "")

    books = Book.objects.exclude(status=BookStatus.DELETED)
    if selected_status:
        if selected_status not in [status.value for status in ACTIVE_BOOK_STATUSES]:
            return HttpResponseBadRequest("Unknown status")
        books = books.filter(status=selected_status)

    years = sorted(
        {
            d.year
            for d in Book.objects.exclude(status=BookStatus.DELETED)
            .filter(Q(finished_at__isnull=False) | Q(started_at__isnull=False))
            .values_list("finished_at", "started_at")
            for d in (d[0] or d[1],)
            if d is not None
        },
        reverse=True,
    )

    if selected_year:
        try:
            year_int = int(selected_year)
            if year_int not in years:
                selected_year = ""
            else:
                books = books.filter(
                    Q(finished_at__year=year_int) | Q(started_at__year=year_int)
                )
        except ValueError:
            selected_year = ""

    counts_by_status = {
        row["status"]: row["total"] for row in books.values("status").annotate(total=Count("id"))
    }
    counts = {
        status.value: counts_by_status.get(status.value, 0) for status in ACTIVE_BOOK_STATUSES
    }

    return render(
        request,
        "reading/book_list.html",
        {
            "books": books,
            "statuses": ACTIVE_BOOK_STATUSES,
            "selected_status": selected_status,
            "selected_year": selected_year,
            "years": years,
            "counts": counts,
            "total_count": books.count(),
        },
    )
