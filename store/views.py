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
from django.db.models import Q



def all_products_view(request):
    category_param = request.GET.get('category')
    search_param = request.GET.get('search')

    queryset = Product.objects.all()

    if category_param:
        queryset = queryset.filter(category__name__iexact=category_param)

    if search_param:
        queryset = queryset.filter(Q(name__icontains=search_param))

    serializer = ProductSerializer(queryset, many=True)
    data = serializer.data
    return JsonResponse(data, safe=False)
    

def all_categories_view(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
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

    # Create a cart for the user
    cart = Cart(user=user)
    cart.save()

    # Log the user in
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)

        # Generate both access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access_token = AccessToken.for_user(user)

        # Create a response with user, access token, refresh token, and cart details
        response_data = {
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'user_id': user.id,
            'username': user.username,
            'cart_id': cart.id,
            'cart_user_id': cart.user.id,
        }

        return JsonResponse(response_data, status=status.HTTP_201_CREATED)

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

        # Retrieve the user's cart
        try:
            cart = Cart.objects.get(user=user)
            cart_id = cart.id
        except Cart.DoesNotExist:
            cart_id = None

        # Create a response with user, access token, refresh token, and cart details
        response_data = {
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'user_id': user.id,
            'username': user.username,
            'cart_id': cart_id,
        }

        return JsonResponse(response_data)

    return JsonResponse({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['POST'])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        user = request.user
    except Exception as e:
        return JsonResponse({'detail': 'Invalid request data'}, status=status.HTTP_400_BAD_REQUEST)

    if refresh_token:
        print('******')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return JsonResponse({'detail': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_items_view(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id)
    except Cart.DoesNotExist:
        return Response({'detail': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    cart_items = CartItem.objects.filter(cart=cart)
    serialized_cart_items = []

    for cart_item in cart_items:
        # Calculate the total price for each item
        total_price = cart_item.product.price * cart_item.quantity

        # Create a dictionary with the item's data
        item_data = {
            'product_id': cart_item.product.id,
            'product_name': cart_item.product.name,
            'quantity': cart_item.quantity,
            'total_price': total_price,
        }

        serialized_cart_items.append(item_data)

    return Response(serialized_cart_items, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, cart_id, product_id):
    try:
        quantity = int(request.data.get('quantity'))
    except (ValueError, TypeError):
        return Response({'detail': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

    cart = Cart.objects.get(id=cart_id)
    product = Product.objects.get(id=product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if quantity > 0:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        if quantity > 0:
            cart_item = CartItem(cart=cart, product=product, quantity=quantity)
            cart_item.save()

    return Response({'detail': 'Cart item updated'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id)
    except Cart.DoesNotExist:
        return Response({'detail': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    cart_items = CartItem.objects.filter(cart=cart)

    for cart_item in cart_items:
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()
        cart_item.delete()

    return Response({'detail': 'Cart cleared and stock updated'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token_view(request):
    try:
        refresh_token = request.data.get('refresh_token')

    except Exception as e:
        return JsonResponse({'detail': 'Invalid request data'}, status=status.HTTP_400_BAD_REQUEST)

    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
        except Exception as e:
            return JsonResponse({'detail': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'access_token': access_token}, status=status.HTTP_200_OK)
    return JsonResponse({'detail': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)