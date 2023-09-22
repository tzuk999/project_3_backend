from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('products/', views.all_products_view, name='all-products'),
    path('categories/', views.all_categories_view, name='all-categories'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout, name='logout'),
    path('cart/<int:cart_id>/', views.cart_items_view, name='cart-items'),
    path('cart/<int:cart_id>/update/<int:product_id>/', views.update_cart_item, name='update-cart-item'),
    path('cart/<int:cart_id>/clear/', views.clear_cart, name='clear-cart'),
    path('refresh-token/', views.refresh_token_view, name='refresh_token'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
