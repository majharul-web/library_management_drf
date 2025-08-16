from rest_framework import serializers
from library.models import Book, Author, Category, BorrowRecord
from django.contrib.auth import get_user_model

class EmptySerializer(serializers.Serializer):
    pass

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']

class BookListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'category', 'ISBN', 'availability_status']
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'category','ISBN', 'availability_status']

class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Simplified user representation showing only `id` and `name`.
    """
    name = serializers.SerializerMethodField(method_name='get_name', help_text="Full name of the user.")

    class Meta:
        model = get_user_model()
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.get_full_name()
    
class BorrowRecordListSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = BorrowRecord
        fields = ['id', 'user', 'book', 'borrow_date', 'return_date', 'is_returned']
        read_only_fields = ['borrow_date', 'is_returned', 'return_date']

class BorrowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRecord
        fields = ['id', 'user', 'book', 'borrow_date', 'return_date', 'is_returned']
        read_only_fields = ['borrow_date', 'is_returned', 'return_date']
