from django.db import models
from django.conf import settings

class Category(models.Model):
    """
    Model representing a book category in the library.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name of the book category (e.g., 'Science Fiction', 'Software Engineering')."
    )

    def __str__(self):
        return self.name


class Author(models.Model):
    """
    Model representing an author.
    """
    name = models.CharField(
        max_length=100,
        help_text="Full name of the author."
    )
    biography = models.TextField(
        blank=True,
        null=True,
        help_text="Optional biography or description of the author."
    )

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Model representing a book in the library.
    """
    title = models.CharField(
        max_length=200,
        help_text="Title of the book."
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="books",
        help_text="Author of the book."
    )
    ISBN = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique International Standard Book Number."
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="books",
        help_text="Category of the book."
    )
    availability_status = models.BooleanField(
        default=True,
        help_text="Availability status: True if available, False if currently borrowed."
    )

    def __str__(self):
        return self.title


class BorrowRecord(models.Model):
    """
    Model representing a record of a book borrowed by a user.
    """
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrow_records",
        help_text="Book being borrowed."
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrow_records",
        help_text="User who borrowed the book."
    )
    borrow_date = models.DateField(
        auto_now_add=True,
        help_text="Date when the book was borrowed."
    )
    return_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when the book was returned (null until returned)."
    )
    is_returned = models.BooleanField(
        default=False,
        help_text="Indicates whether the book has been returned."
    )

    def __str__(self):
        return f"{self.user.email} borrowed {self.book.title}"
