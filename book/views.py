
from book.models import *
from book.serializers import *
from django.db.models import Count
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from book.filters import BookFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from book.paginations import DefaultPagination
from api.permissions import IsAdminOrReadOnly
from drf_yasg.utils import swagger_auto_schema


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter
    pagination_class = DefaultPagination
    search_fields = ['title','category__name','author__name','isbn']
    ordering_fields = ['price', 'updated_at']
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(
        operation_summary='Retrive a list of books'
    )
    def list(self, request, *args, **kwargs):
        """Retrive all the books"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a book by admin",
        operation_description="This allow an admin to create a book",
        request_body=BookSerializer,
        responses={
            201: BookSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        """Only authenticated admin can create book"""
        return super().create(request, *args, **kwargs)


class BookImageViewSet(ModelViewSet):
    serializer_class = BookImageSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return BookImage.objects.filter(book_id=self.kwargs.get('book_pk'))

    def perform_create(self, serializer):
        serializer.save(book_id=self.kwargs.get('book_pk'))


class CategoryViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.annotate(
        book_count=Count('books')).all()
    serializer_class = CategorySerializer
