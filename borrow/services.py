from borrow.models import Cart, CartItem, Borrow, BorrowItem
from book.models import Book
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError


class BorrowService:
    @staticmethod
    # In borrow/services.py

    def create_borrow(cart_id, user_id):
        cart = Cart.objects.get(id=cart_id, user_id=user_id)
        cart_items = cart.items.select_related('book')
        
        # Check if cart is empty
        if not cart_items.exists():
            raise ValueError("Cart is empty")
        
        # Check availability for ALL books in cart
        for item in cart_items:
            if item.book.availability_status != 'available':
                raise ValueError(f"Book '{item.book.title}' is not available")
        
        # Use transaction to ensure all-or-nothing
        with transaction.atomic():
            # Create the main Borrow record
            borrow = Borrow.objects.create(
                user_id=user_id,
                status='keeping'
            )
            
            # Create BorrowItem records for each cart item
            for item in cart_items:
                BorrowItem.objects.create(
                    borrow=borrow,  # Link to the main borrow
                    book=item.book,
                    quantity=item.quantity,
                    returned=False
                )
                
                # Update book availability
                item.book.availability_status = 'borrowed'
                item.book.save()
            
            # Clear the cart after successful borrow
            cart_items.delete()
        
        return borrow

    @staticmethod
    def cancel_borrow(borrow, user):
        if user.is_staff:
            borrow.status = Borrow.CANCELED
            borrow.save()
            return borrow

        if borrow.user != user:
            raise PermissionDenied(
                {"detail": "You can only cancel your own borrow"})

        if borrow.status == Borrow.DELIVERED:
            raise ValidationError({"detail": "You can not cancel a borrow"})

        borrow.status = Borrow.CANCELED
        borrow.save()
        return borrow


"""
Transaction
A       B
100
0     
        400
"""