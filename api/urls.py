from django.urls import path, include
from book.views import *
from borrow.views import *
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('books', BookViewSet, basename='books')
router.register('categories', CategoryViewSet)
# router.register('carts', CartViewSet, basename='carts')
# router.register('orders', OrderViewset, basename='orders')

book_router = routers.NestedDefaultRouter(
    router, 'books', lookup='book')
book_router.register('images', BookImageViewSet,
                     basename='book-images')

# cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
# cart_router.register('items', CartItemViewSet, basename='cart-item')

# urlpatterns = router.urls

urlpatterns = [
    path('', include(router.urls)),
    path('', include(book_router.urls)),
    # path('', include(cart_router.urls)),
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.jwt')),
]