from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import User
import json
from rest_framework.permissions import IsAuthenticated



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


@api_view(['POST'])
def signup(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)

    if not username or not password:
        return JsonResponse({'detail': 'Both username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'detail': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User(username=username)
    user.set_password(password)
    user.save()

    # Log the user in
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)

        # Generate both access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access_token = AccessToken.for_user(user)

        return JsonResponse({
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'user_id': user.id,
            'username': user.username,
        }, status=status.HTTP_201_CREATED)

    return JsonResponse({'detail': 'User creation failed'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def signin(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is not None:
        # Log the user in
        login(request, user)

        # Generate both access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access_token = AccessToken.for_user(user)

        return JsonResponse({
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'user_id': user.id,
            'username': user.username,
        })

    return JsonResponse({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        user = request.user
    except Exception as e:
        return JsonResponse({'detail': 'Invalid request data'}, status=status.HTTP_400_BAD_REQUEST)

    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return JsonResponse({'detail': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)
