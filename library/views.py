from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from library.models import Book, Author, Category, BorrowRecord
from library.serializers import BookSerializer, AuthorSerializer, CategorySerializer, BorrowRecordSerializer
from django.utils import timezone

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return BorrowRecord.objects.all()
        return BorrowRecord.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        book_id = request.data.get('book')
        book = Book.objects.get(id=book_id)
        if not book.availability_status:
            return Response({"error": "Book not available"}, status=status.HTTP_400_BAD_REQUEST)
        book.availability_status = False
        book.save()
        record = BorrowRecord.objects.create(book=book, user=request.user)
        serializer = self.get_serializer(record)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def return_book(self, request, pk=None):
        borrow = self.get_object()
        if borrow.user != request.user and request.user.role != 'admin':
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        borrow.is_returned = True
        borrow.return_date = timezone.now()
        borrow.book.availability_status = True
        borrow.book.save()
        borrow.save()
        return Response({"status": "Book returned"})
