from borrow.models import Cart, CartItem, Borrow, BorrowItem
from book.models import Book
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError


class BorrowService:
    @staticmethod
    def create_borrow(user_id, cart_id):
        with transaction.atomic():
            cart = Cart.objects.get(pk=cart_id)
            cart_items = cart.items.select_related('book').all()

            total_price = sum([item.book.price *
                               item.quantity for item in cart_items])

            borrow = Borrow.objects.create(
                user_id=user_id, total_price=total_price)

            borrow_items = [
                BorrowItem(
                    borrow=borrow,
                    book=item.book,
                    price=item.book.price,
                    quantity=item.quantity,
                    total_price=item.book.price * item.quantity
                )
                for item in cart_items
            ]
            # [<BorrowItem(1)>, <BorrowItem(2)>]
            BorrowItem.objects.bulk_create(borrow_items)

            cart.delete()

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