from django.urls import path

from . import views

urlpatterns = [
    path("", views.book_list, name="book-list"),
    path("books/new/", views.BookCreateView.as_view(), name="book-create"),
    path("books/<int:pk>/edit/", views.BookUpdateView.as_view(), name="book-update"),
    path("books/<int:pk>/delete/", views.BookDeleteView.as_view(), name="book-delete"),
    path("books/<int:pk>/status/", views.update_status, name="book-status"),
]
