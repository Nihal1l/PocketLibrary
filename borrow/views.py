from django.shortcuts import render
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from borrow import serializers as borrowSz
from borrow.serializers import CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from borrow.models import Cart, CartItem, Borrow, BorrowItem
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from borrow.services import BorrowService
from rest_framework.response import Response


class CartViewSet(ModelViewSet):
    http_method_names = ['get', 'post']
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    # def create(self, request, *args, **kwargs):
    #     if self.request.user:
    #         return super().create(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.prefetch_related('items__book').filter(user=self.request.user)

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context

        return {'cart_id': self.kwargs.get('cart_pk')}

    def get_queryset(self):
        return CartItem.objects.select_related('book').filter(cart_id=self.kwargs.get('cart_pk'))


class BorrowViewset(ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'put', 'head', 'options']

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        borrow = self.get_object() 
        BorrowService.cancel_borrow(borrow=borrow, user=request.user)
        return Response({'status': 'Borrow canceled'})

    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None):
        borrow = self.get_object()
        serializer = borrowSz.UpdateBorrowSerializer(
            borrow, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': f'borrow status updated to {request.data['status']}'})

    def get_permissions(self):
        if self.action in ['update_status', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'cancel':
            return borrowSz.EmptySerializer
        if self.action == 'create':
            return borrowSz.CreateBorrowSerializer
        elif self.action == 'update_status':
            return borrowSz.UpdateBorrowSerializer
        return borrowSz.BorrowSerializer

    def get_serializer_context(self):
        if getattr(self, 'swagger_fake_view', False):
            return super().get_serializer_context()
        return {'user_id': self.request.user.id, 'user': self.request.user}

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Borrow.objects.none()
        if self.request.user.is_staff:
            return Borrow.objects.prefetch_related('items__book').all()
        return Borrow.objects.prefetch_related('items__book').filter(user=self.request.user)