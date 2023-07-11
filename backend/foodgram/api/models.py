from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from .constants import Constants

User = get_user_model()


class Tag(models.Model):
    """Модель тэга."""
    name = models.CharField(null=False, blank=False,
                            unique=True,
                            max_length=Constants.MAX_TAG_NAME,
                            verbose_name='Название')
    color = models.CharField(null=False, blank=False,
                             unique=True,
                             max_length=Constants.MAX_TAG_COLOR,
                             verbose_name='Цвет')
    slug = models.SlugField(null=False, blank=False,
                            unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиента."""
    name = models.CharField(null=False, blank=False,
                            max_length=Constants.MAX_ING_NAME,
                            verbose_name='Название')
    measurement_unit = models.CharField(null=False,
                                        blank=False,
                                        max_length=Constants.MAX_ING_UNIT,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    name = models.CharField(null=False, blank=False,
                            max_length=Constants.MAX_RECIPE_NAME,
                            verbose_name='Название')
    image = models.ImageField(upload_to='recipes/', null=False, blank=False)
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='AmountOfIngredients', verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')
    cooking_time = models.PositiveIntegerField(validators=[MinValueValidator(
        1, message='Минимальное значение 1')],
        verbose_name='Время готовки')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class AmountOfIngredients(models.Model):
    """Модель ингридиентов в рецепте."""
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, verbose_name='Рецепт')
    amount = models.PositiveIntegerField(validators=[MinValueValidator(
        1, message='Минимальное значение 1')], verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe.name}: {self.amount} {self.ingredient.name}'


class Favorite(models.Model):
    """Модель избранных."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в избранное'


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'В корзине'

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в корзину'
