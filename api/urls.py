from django.urls import path, include
from rest_framework_nested import routers
from library.views import BookViewSet, AuthorViewSet, CategoryViewSet, BorrowRecordViewSet


# main router
router = routers.DefaultRouter()
router.register('books', BookViewSet)
router.register('authors', AuthorViewSet)
router.register('categories', CategoryViewSet)
router.register('borrow', BorrowRecordViewSet)

# Nested routers
books_router = routers.NestedDefaultRouter(router, 'books', lookup='book')
books_router.register('borrow', BorrowRecordViewSet, basename='book-borrow')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(books_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
