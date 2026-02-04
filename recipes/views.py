from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Recipe, RecipeIngredient
from .serializers import RecipeSerializer, RecipeIngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Рецепты для групп пользователя"""
        group_id = self.request.query_params.get('group')
        queryset = Recipe.objects.filter(group__members=self.request.user)
        
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        
        return queryset

    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """Закрепить/открепить рецепт"""
        recipe = self.get_object()
        recipe.is_pinned = not recipe.is_pinned
        recipe.save()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeIngredientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Ингредиенты рецептов для групп пользователя"""
        recipe_id = self.request.query_params.get('recipe')
        queryset = RecipeIngredient.objects.filter(
            recipe__group__members=self.request.user
        )
        
        if recipe_id:
            queryset = queryset.filter(recipe_id=recipe_id)
        
        return queryset

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Изменить порядок ингредиентов"""
        ingredients_order = request.data.get('ingredients', [])
        for ingredient_data in ingredients_order:
            RecipeIngredient.objects.filter(id=ingredient_data['id']).update(order=ingredient_data['order'])
        return Response({"status": "reordered"})
