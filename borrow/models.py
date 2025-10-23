from uuid import uuid4
from django.db import models
from book.models import Book
from users.models import User
from django.core.validators import MinValueValidator

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.first_name}"

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [['cart', 'book']]

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"

class Borrow(models.Model):
    """
    Represents completed book borrowing transactions.
    """
    STATUS_CHOICES = [
        ('keeping', 'Keeping'),
        ('returned', 'Returned')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='borrows'
    )
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='keeping'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Borrow #{self.id} by {self.user.email}"


class BorrowItem(models.Model):
    """
    Contains details about items in a borrow transaction.
    """
    borrow = models.ForeignKey(
        Borrow,
        on_delete=models.CASCADE,
        related_name='items'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='borrow_items'
    )
    quantity = models.IntegerField(default=1)
    returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.book.title} in Borrow #{self.borrow.id}"

