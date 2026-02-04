from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ShoppingList, ShoppingItem
from .serializers import ShoppingListSerializer, ShoppingItemSerializer

class ShoppingListViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.request.query_params.get('group')
        queryset = ShoppingList.objects.filter(group__members=self.request.user)
        
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        
        return queryset

    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        shopping_list = self.get_object()
        shopping_list.is_pinned = not shopping_list.is_pinned
        shopping_list.save()
        serializer = self.get_serializer(shopping_list)
        return Response(serializer.data)


class ShoppingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        shopping_list_id = self.request.query_params.get('shopping_list')
        queryset = ShoppingItem.objects.filter(
            shopping_list__group__members=self.request.user
        )
        
        if shopping_list_id:
            queryset = queryset.filter(shopping_list_id=shopping_list_id)
        
        return queryset

    def create(self, request, *args, **kwargs):
        shopping_list_id = request.data.get('shopping_list')
        if not shopping_list_id:
            return Response(
                {"error": "shopping_list обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            shopping_list = ShoppingList.objects.get(
                id=shopping_list_id,
                group__members=request.user
            )
        except ShoppingList.DoesNotExist:
            return Response(
                {"error": "Список покупок не найден или нет доступа"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_check(self, request, pk=None):
        item = self.get_object()
        item.is_checked = not item.is_checked
        item.save()
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """НОВЫЙ ENDPOINT: Закрепить/открепить товар"""
        item = self.get_object()
        item.is_pinned = not item.is_pinned
        item.save()
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        items_order = request.data.get('items', [])
        for item_data in items_order:
            ShoppingItem.objects.filter(id=item_data['id']).update(order=item_data['order'])
        return Response({"status": "reordered"})
