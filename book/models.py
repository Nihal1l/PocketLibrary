from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from users.models import User, Author
from book.validators import validate_file_size

class Category(models.Model):
    """
    Groups books into categories.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
    ]

    title = models.CharField(max_length=300)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books'
    )
    isbn = models.CharField(max_length=13, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='books'
    )
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-id',]
        
    def __str__(self):
        return f"{self.title} by {self.author.name}"

class BookImage(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to="books/images/", validators=[validate_file_size])
    # file = models.FileField(upload_to="book/files",