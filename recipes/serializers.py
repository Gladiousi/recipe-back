from rest_framework import serializers
from .models import Recipe, RecipeIngredient
from users.serializers import UserSerializer

class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'quantity', 'unit', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'group', 'title', 'description', 'image', 'cooking_time', 'servings', 'is_pinned', 'ingredients', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class RecipeDetailSerializer(RecipeSerializer):
    """Более детальный сериализатор для одного рецепта"""
    pass
