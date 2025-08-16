from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from library.models import Book, Author, Category, BorrowRecord
from library.serializers import (
    BookSerializer, AuthorSerializer, CategorySerializer,
    BorrowRecordSerializer, EmptySerializer, BookListSerializer, BorrowRecordListSerializer
)


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to allow only the owner of a borrow record
    or an admin (librarian) to perform restricted actions.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin' or obj.user == request.user


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing book categories.
    - Librarians (admin) can create, update, or delete categories.
    - Authenticated users can view categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class AuthorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing authors.
    - Librarians (admin) can create, update, or delete authors.
    - Authenticated users can view authors.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing books.
    - Librarians (admin) can add, update, or delete books.
    - Authenticated members can only view and borrow/return books.
    """
    queryset = Book.objects.select_related('author', 'category').all()

    def get_serializer_class(self):
        if self.action in ['borrow_book', 'make_available']:
            return EmptySerializer
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'make_available']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="Borrow a book. User cannot borrow the same book twice without returning it first.",
        responses={
            201: BorrowRecordSerializer(),
            400: "Book not available or already borrowed"
        }
    )
    @action(detail=True, methods=['post'])
    def borrow_book(self, request, pk=None):
        """
        Borrow a book if available.
        """
        book = self.get_object()

        if not book.availability_status:
            return Response({"error": "Book not available"}, status=status.HTTP_400_BAD_REQUEST)

        if BorrowRecord.objects.filter(book=book, user=request.user, is_returned=False).exists():
            return Response({"error": "You already borrowed this book and have not returned it"},
                            status=status.HTTP_400_BAD_REQUEST)

        book.availability_status = False
        book.save()
        record = BorrowRecord.objects.create(book=book, user=request.user)
        return Response({"status": "Book borrowed successfully"}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Mark a book as available again (admin only).",
        responses={
            200: "Book marked available",
            400: "Book already available"
        }
    )
    @action(detail=True, methods=['post'])
    def make_available(self, request, pk=None):
        """
        Mark a book as available (admin only).
        """
        book = self.get_object()
        if book.availability_status:
            return Response({"error": "Book already available"}, status=status.HTTP_400_BAD_REQUEST)
        book.availability_status = True
        book.save()
        return Response({"status": "Book is now available"}, status=status.HTTP_200_OK)


class BorrowRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing borrow records.
    - Members can see and return their own borrow records.
    - Admin can view/manage all borrow records.
    """
    queryset = BorrowRecord.objects.all()

    def get_serializer_class(self):
        if self.action == 'return_book':
            return EmptySerializer
        if self.action == 'list':
            return BorrowRecordListSerializer
        return BorrowRecordSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Filter records:
        - Admin sees all
        - Member sees only their own
        """
        user = self.request.user
        return BorrowRecord.objects.all() if user.role == 'admin' else BorrowRecord.objects.filter(user=user)

    @swagger_auto_schema(
        operation_description="Borrow a book by specifying its ID. Fails if not available or already borrowed.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['book'],
            properties={
                'book': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the book to borrow"),
            },
        ),
        responses={201: BorrowRecordSerializer(), 400: "Book not available or already borrowed"}
    )
    def create(self, request, *args, **kwargs):
        """
        Borrow a book by providing its ID.
        """
        book_id = request.data.get('book')
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        if not book.availability_status:
            return Response({"error": "Book not available"}, status=status.HTTP_400_BAD_REQUEST)

        if BorrowRecord.objects.filter(book=book, user=request.user, is_returned=False).exists():
            return Response({"error": "You already borrowed this book and not returned it"},
                            status=status.HTTP_400_BAD_REQUEST)

        book.availability_status = False
        book.save()
        record = BorrowRecord.objects.create(book=book, user=request.user)
        return Response({"status": "Book borrowed successfully"}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Return a borrowed book. Only borrower or admin can do this.",
        responses={
            200: "Book returned successfully",
            400: "Book already returned",
            403: "Not allowed"
        }
    )
    @action(detail=True, methods=['post'], url_path='return')
    def return_book(self, request, pk=None):
        """
        Return a borrowed book (by borrower or admin).
        """
        borrow = self.get_object()

        if borrow.user != request.user and request.user.role != 'admin':
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        if borrow.is_returned:
            return Response({"error": "Book already returned"}, status=status.HTTP_400_BAD_REQUEST)

        borrow.is_returned = True
        borrow.return_date = timezone.now()
        borrow.book.availability_status = True
        borrow.book.save()
        borrow.save()
        return Response({"status": "Book returned successfully"}, status=status.HTTP_200_OK)
