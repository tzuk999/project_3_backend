from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    number_of_products = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    products = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'