from rest_framework import serializers
from borrow.models import Cart, CartItem, Borrow, BorrowItem
from book.models import Book
from book.serializers import BookSerializer, SimpleUserSerializer
from borrow.serializers import BorrowSerializer
from borrow.services import BorrowService


class EmptySerializer(serializers.Serializer):
    pass


class SimpleBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'availability_status']


class AddCartItemSerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['id', 'book_id', 'quantity']

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        book_id = self.validated_data['book_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, book_id=book_id)
            cart_item.quantity += quantity
            self.instance = cart_item.save()
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    def validate_book_id(self, value):
        if not Book.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                f"Book with id {value} does not exists")
        return value


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CartItemSerializer(serializers.ModelSerializer):
    book = SimpleBookSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'book', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']
        read_only_fields = ['user']



class CreateBorrowSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart found with this id')

        if not CartItem.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError('Cart is empty')

        return cart_id

    def create(self, validated_data):
        user_id = self.context['user_id']
        cart_id = validated_data['cart_id']

        try:
            borrow = BorrowService.create_order(user_id=user_id, cart_id=cart_id)
            return borrow
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def to_representation(self, instance):
        return BorrowSerializer(instance).data


class BorrowItemSerializer(serializers.ModelSerializer):
    book = SimpleBookSerializer()

    class Meta:
        model = BorrowItem
        fields = ['id', 'book', 'quantity']


class UpdateBorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['status']


class BorrowSerializer(serializers.ModelSerializer):
    items = BorrowItemSerializer(many=True)

    class Meta:
        model = Borrow
        fields = ['id', 'user', 'status', 'created_at', 'items']