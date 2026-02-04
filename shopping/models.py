from django.db import models
from django.conf import settings
from groups.models import Group

class ShoppingList(models.Model):
    """Список покупок для группы"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='shopping_lists')
    name = models.CharField(max_length=255, default='Список покупок')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_shopping_lists'
    )
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.group.name}"

    class Meta:
        ordering = ['-is_pinned', '-updated_at']


class ShoppingItem(models.Model):
    """Элемент списка покупок"""
    UNIT_CHOICES = [
        ('', 'Без единиц'),
        ('pcs', 'Штук'),
        ('kg', 'Килограмм'),
        ('g', 'Грамм'),
        ('l', 'Литров'),
        ('ml', 'Миллилитров'),
    ]

    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE,
        related_name='items'
    )
    name = models.CharField(max_length=255)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, blank=True, default='')
    is_checked = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)  # НОВОЕ ПОЛЕ!
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_shopping_items'
    )
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-is_pinned', 'order', 'created_at']  # Закрепленные сверху
