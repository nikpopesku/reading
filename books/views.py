from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import BookForm
from .models import ACTIVE_BOOK_STATUSES, Book, BookStatus


@login_required
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


class ActiveBookQuerySetMixin:
    def get_queryset(self):
        return Book.objects.exclude(status=BookStatus.DELETED)


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("book-list")


class BookUpdateView(LoginRequiredMixin, ActiveBookQuerySetMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("book-list")


class BookDeleteView(LoginRequiredMixin, ActiveBookQuerySetMixin, DeleteView):
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("book-list")

    def form_valid(self, form):
        self.object.status = BookStatus.DELETED
        self.object.save(update_fields=["status", "updated_at"])
        return HttpResponseRedirect(self.get_success_url())


@login_required
@require_POST
def update_status(request, pk: int):
    status = request.POST.get("status")
    if status not in [status.value for status in ACTIVE_BOOK_STATUSES]:
        return HttpResponseBadRequest("Unknown status")

    book = get_object_or_404(Book, pk=pk, status__in=ACTIVE_BOOK_STATUSES)
    today = timezone.localdate()
    book.status = status
    if status == BookStatus.READING and book.started_at is None:
        book.started_at = today
    if status == BookStatus.READ:
        if book.started_at is None:
            book.started_at = today
        if book.finished_at is None:
            book.finished_at = today
    book.save()

    return render(
        request, "books/_book_card.html", {"book": book, "statuses": ACTIVE_BOOK_STATUSES}
    )
