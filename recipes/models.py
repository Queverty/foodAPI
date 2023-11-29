from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from user.models import User

# Create your models here.

class Ingredients(models.Model):
	name = models.CharField(unique=True, max_length=255,
							verbose_name='Название')
	measurement_unit = models.CharField(unique=True, max_length=255,
										verbose_name='Единица измерения')

	class Meta:
		verbose_name = 'Ингредиент'
		verbose_name_plural = 'Ингредиенты'
		ordering = ['name']

	def __str__(self):
		return f'{self.name}, {self.measurement_unit}'


class Tegs(models.Model):
	name = models.CharField(unique=True, max_length=200,
							verbose_name='Название')

	hex_color = models.CharField(
		max_length=7,
		validators=[RegexValidator(r'^#[A-Fa-f0-9]{6}$')],
		verbose_name='Цветовой HEX-код',
		unique=True,
	)
	slug = models.SlugField(unique=True, max_length=200, verbose_name='слаг')

	class Meta:
		verbose_name = 'Тег'
		verbose_name_plural = 'Теги'

	def __str__(self):
		return self.name


class Recipes(models.Model):
	tags = models.ManyToManyField(Tegs,
								  verbose_name='Теги')
	author = models.ForeignKey(User,
							   on_delete=models.CASCADE,
							   verbose_name="Автор")
	ingredients = models.ManyToManyField(to=Ingredients,
										 through='IngredientAmmount',
										 verbose_name='Ингредиенты')
	is_favorited = models.BooleanField(default=False)
	is_in_shopping_cart = models.BooleanField(default=False)
	name = models.CharField(max_length=200, verbose_name="Название")
	image = models.ImageField(upload_to='recipes/%Y/%m/%d/',
							  verbose_name="Изображение")
	text = models.CharField(verbose_name="Описание")
	cooking_time = models.PositiveIntegerField(
		verbose_name="Время приготовления",
		validators=[MinValueValidator(1,
									  message='Минимальное значение 1!')])

	class Meta:
		ordering = ['-id']
		verbose_name = 'Рецепт'
		verbose_name_plural = 'Рецепты'

	def __str__(self):
		return self.name


class IngredientAmmount(models.Model):
	recipes = models.ForeignKey(Recipes, on_delete=models.CASCADE)
	ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
	ammount = models.PositiveIntegerField(
		validators=[MinValueValidator(1,
									  message='Минимальное значение 1!')])


class Favorite(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE,
							 verbose_name='Пользователь')
	recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE,
							   verbose_name='Рецепт')

	class Meta:
		ordering = ['-id']
		verbose_name = 'Избранное'
		verbose_name_plural = 'Избранные рецепты'

	def __str__(self):
		return f'{self.user} добавил "{self.recipe}" в избранное'


class ShoppingCart(models.Model):
	user = models.ForeignKey(User,
							 on_delete=models.CASCADE,
							 verbose_name='Пользователь')
	recipe = models.ForeignKey(Recipes,
							   on_delete=models.CASCADE,
							   verbose_name='Рецепт')

	class Meta:
		ordering = ['-id']
		verbose_name = 'Корзина покупок'
		verbose_name_plural = 'Корзина покупок'

	def __str__(self):
		return f'{self.user} добавил "{self.recipe}" в корзину покупок'
