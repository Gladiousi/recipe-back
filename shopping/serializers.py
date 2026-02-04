from rest_framework import serializers
from .models import ShoppingList, ShoppingItem
from users.serializers import UserSerializer

class ShoppingItemSerializer(serializers.ModelSerializer):
    added_by = UserSerializer(read_only=True)

    class Meta:
        model = ShoppingItem
        fields = ['id', 'shopping_list', 'name', 'quantity', 'unit', 'is_checked', 'is_pinned', 'added_by', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'added_by', 'created_at', 'updated_at']

    def validate_unit(self, value):
        if value is None:
            return ''
        return value


class ShoppingListSerializer(serializers.ModelSerializer):
    items = ShoppingItemSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    items_count = serializers.SerializerMethodField()
    checked_count = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingList
        fields = ['id', 'group', 'name', 'is_pinned', 'items', 'items_count', 'checked_count', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_items_count(self, obj):
        return obj.items.count()

    def get_checked_count(self, obj):
        return obj.items.filter(is_checked=True).count()

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
