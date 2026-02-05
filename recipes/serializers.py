import json
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
        fields = [
            'id', 'group', 'title', 'description', 'image', 'cooking_time', 
            'servings', 'is_pinned', 'ingredients', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        
        # Парсим JSON ингредиенты
        ingredients_json = self.initial_data.get('ingredients', '[]')
        try:
            ingredients_data = json.loads(ingredients_json) if ingredients_json else []
        except json.JSONDecodeError:
            ingredients_data = []
        
        recipe = super().create(validated_data)
        
        # Bulk create ингредиентов
        for order, ing_data in enumerate(ingredients_data):
            RecipeIngredient.objects.create(
                recipe=recipe,
                name=ing_data['name'],
                quantity=ing_data.get('quantity'),
                unit=ing_data.get('unit', ''),
                order=order
            )
        
        return recipe

    def update(self, instance, validated_data):
        # Парсим JSON ингредиенты
        ingredients_json = self.initial_data.get('ingredients', '[]')
        try:
            ingredients_data = json.loads(ingredients_json) if ingredients_json else []
        except json.JSONDecodeError:
            ingredients_data = []
        
        # Обновляем рецепт
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.servings = validated_data.get('servings', instance.servings)
        instance.save()
        
        # Перезаписываем ингредиенты
        instance.ingredients.all().delete()
        for order, ing_data in enumerate(ingredients_data):
            RecipeIngredient.objects.create(
                recipe=instance,
                name=ing_data['name'],
                quantity=ing_data.get('quantity'),
                unit=ing_data.get('unit', ''),
                order=order
            )
        
        return instance
