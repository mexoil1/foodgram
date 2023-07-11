from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http.response import HttpResponse
from django.db.models import Sum

from .filters import IngredientFilter, RecipeFilter
from .models import (AmountOfIngredients, Favorite, Ingredient,
                     Recipes, ShoppingCart, Tag)
from .pagination import LimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = IngredientFilter
    search_fields = ('^name',)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPagination
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранные."""
        if request.method == 'POST':
            if Favorite.objects.filter(user=request.user,
                                       recipe__id=pk).exists():
                return Response({
                    'errors': 'Рецепт добавлен в список'
                }, status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipes, id=pk)
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe = Favorite.objects.filter(user=request.user, recipe__id=pk)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в корзину."""
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user,
                                           recipe__id=pk).exists():
                return Response({
                    'errors': 'Рецепт добавлен в список'
                }, status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipes, id=pk)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe = ShoppingCart.objects.filter(
            user=request.user, recipe__id=pk)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивание корзины."""
        ingredients = AmountOfIngredients.objects.filter(
            recipe__cart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = 'Купить в магазине:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        shopping_list += '\n© самый лучший разработчик Слукин Михаил'
        file = 'shopping_cart'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response
