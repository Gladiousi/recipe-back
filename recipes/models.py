from django.db import models
from django.conf import settings
from groups.models import Group

class Recipe(models.Model):
    """Рецепт"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=255)
    description = models.TextField(help_text='Поддерживает Markdown')
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    cooking_time = models.IntegerField(help_text='Время в минутах', blank=True, null=True)
    servings = models.IntegerField(help_text='Количество порций', blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_recipes'
    )
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-is_pinned', '-created_at']


class RecipeIngredient(models.Model):
    """Ингредиент рецепта"""
    UNIT_CHOICES = [
        ('', 'По вкусу'),
        ('pcs', 'Штук'),
        ('kg', 'Килограмм'),
        ('g', 'Грамм'),
        ('l', 'Литров'),
        ('ml', 'Миллилитров'),
        ('tbsp', 'Столовых ложек'),
        ('tsp', 'Чайных ложек'),
        ('cup', 'Стаканов'),
    ]

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=255)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, blank=True, default='')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.recipe.title}"

    class Meta:
        ordering = ['order', 'created_at']
