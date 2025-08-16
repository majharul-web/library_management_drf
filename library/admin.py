from django.contrib import admin
from library.models import Book, Author, Category, BorrowRecord

# Register your models here.

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(BorrowRecord)