from rest_framework.routers import DefaultRouter
from django.urls import path, include
from library.views import BookViewSet, AuthorViewSet, CategoryViewSet, BorrowRecordViewSet

router = DefaultRouter()
router.register('books', BookViewSet)
router.register('authors', AuthorViewSet)
router.register('categories', CategoryViewSet)
router.register('borrow', BorrowRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
