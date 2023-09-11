from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.all_products_view, name='all-products'),
    path('categories/', views.all_categories_view, name='all-categories'),
    path('cart/<int:user_id>/', views.cart_by_user_view, name='cart-by-user'),
]
