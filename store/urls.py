from django.urls import path
from .views import AllProductsView, AllCategoriesView, CartByUserView

urlpatterns = [
    path('products/', AllProductsView.as_view(), name='all-products'),
    path('categories/', AllCategoriesView.as_view(), name='all-categories'),
    path('cart/<int:user_id>/', CartByUserView.as_view(), name='cart-by-user'),
]