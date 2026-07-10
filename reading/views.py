from django.db.models import Case, Count, F, IntegerField, Q, Value, When
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from .models import ACTIVE_BOOK_STATUSES, Book, BookStatus


def _build_querystring(request, **updates):
    params = request.GET.copy()
    for key, value in updates.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value

    query_string = params.urlencode()
    return f"{request.path}?{query_string}" if query_string else request.path


def _sort_link(request, selected_sort, field):
    is_active = selected_sort.lstrip("-") == field
    next_sort = f"-{field}" if selected_sort == field else field
    aria_sort = (
        "ascending"
        if selected_sort == field
        else "descending"
        if selected_sort == f"-{field}"
        else "none"
    )
    direction = "▲" if selected_sort == field else "▼" if selected_sort == f"-{field}" else "↕"
    return {
        "url": _build_querystring(request, sort=next_sort),
        "aria_sort": aria_sort,
        "direction": direction,
        "is_active": is_active,
    }


def book_list(request):
    selected_status = request.GET.get("status", "")
    selected_year = request.GET.get("year", "")
    selected_sort = request.GET.get("sort", "")

    books = Book.objects.exclude(status=BookStatus.DELETED).prefetch_related("tags")
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
                books = books.filter(Q(finished_at__year=year_int) | Q(started_at__year=year_int))
        except ValueError:
            selected_year = ""

    status_order = Case(
        When(status=BookStatus.WILL_READ, then=Value(0)),
        When(status=BookStatus.READING, then=Value(1)),
        When(status=BookStatus.READ, then=Value(2)),
        output_field=IntegerField(),
    )

    if selected_sort == "title":
        books = books.order_by("title")
    elif selected_sort == "-title":
        books = books.order_by("-title")
    elif selected_sort == "author":
        books = books.order_by("author", "title")
    elif selected_sort == "-author":
        books = books.order_by("-author", "title")
    elif selected_sort == "status":
        books = books.order_by(status_order, "title")
    elif selected_sort == "-status":
        books = books.order_by(status_order.desc(), "title")
    elif selected_sort == "started_at":
        books = books.order_by(F("started_at").asc(nulls_last=True), "title")
    elif selected_sort == "-started_at":
        books = books.order_by(F("started_at").desc(nulls_last=True), "title")
    elif selected_sort == "finished_at":
        books = books.order_by(F("finished_at").asc(nulls_last=True), "title")
    elif selected_sort == "-finished_at":
        books = books.order_by(F("finished_at").desc(nulls_last=True), "title")
    elif selected_sort == "rating":
        books = books.order_by(F("rating").asc(nulls_last=True), "title")
    elif selected_sort == "-rating":
        books = books.order_by(F("rating").desc(nulls_last=True), "title")
    else:
        books = books.order_by(status_order, "title")

    counts_by_status = {
        row["status"]: row["total"]
        for row in books.order_by().values("status").annotate(total=Count("id"))
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
            "selected_sort": selected_sort,
            "sort_links": {
                "title": _sort_link(request, selected_sort, "title"),
                "author": _sort_link(request, selected_sort, "author"),
                "status": _sort_link(request, selected_sort, "status"),
                "started_at": _sort_link(request, selected_sort, "started_at"),
                "finished_at": _sort_link(request, selected_sort, "finished_at"),
                "rating": _sort_link(request, selected_sort, "rating"),
            },
            "years": years,
            "counts": counts,
            "total_count": books.count(),
        },
    )
