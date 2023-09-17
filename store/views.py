from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *


def all_products_view(request):
    try:
        products = Product.objects.all()
    except Product.DoesNotExist:
        raise Http404("No products found.")

    serializer = ProductSerializer(products, many=True)
    data = serializer.data
    return JsonResponse(data, safe=False)
    

def all_categories_view(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    data = serializer.data
    return JsonResponse(data, safe=False)
    

def cart_by_user_view(request, user_id):
    try:
        cart = Cart.objects.get(user_id=user_id)
    except Cart.DoesNotExist:
        return JsonResponse({'error': 'Cart not found'}, status=404)

    serializer = CartSerializer(cart)
    data = serializer.data
    return JsonResponse(data, safe=False)

def products_by_category_view(request, category_name):
    try:
        products = Product.objects.filter(category__name=category_name)
    except Product.DoesNotExist:
        raise Http404("No products found in this category.")

    serializer = ProductSerializer(products, many=True)
    data = serializer.data
    return JsonResponse(data, safe=False)