from django.contrib.auth.password_validation import validate_password
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueValidator

from recipes.models import (Favorite, IngredientAmmount, Ingredients, Recipes,
                            ShoppingCart, Tegs)
from user.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
	is_subscribed = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = (
			'email', 'id', 'username', 'first_name',
			'last_name', 'is_subscribed')
		extra_kwargs = {'first_name': {'required': True},
						'last_name': {'required': True}}

	def get_is_subscribed(self, obj):
		request_user = self.context.get('request_user', None).id
		users = Follow.objects.filter(author=obj, user=request_user).exists()
		return users


class UserRegistrationSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(max_length=150,
								   required=True,
								   validators=[UniqueValidator(
									   queryset=User.objects.all())]
								   )
	username = serializers.CharField(max_length=150,
									 required=True,
									 validators=[UniqueValidator(
										 queryset=User.objects.all())]
									 )
	password = serializers.CharField(required=True, min_length=8,
									 max_length=150
									 , validators=[validate_password])
	first_name = serializers.CharField(required=True, max_length=150)
	last_name = serializers.CharField(required=True, max_length=150)

	class Meta:
		model = User
		fields = (
			'email', 'username', 'first_name', 'last_name', 'password')

	def create(self, validated_data):
		user = User(username=validated_data["username"],
					email=validated_data["email"],
					first_name=validated_data['first_name'],
					last_name=validated_data['last_name'],
					password=validated_data['password'],
					)
		user.set_password(validated_data['password'])
		user.save()
		return user


class ChangePasswordSerializer(serializers.Serializer):
	current_password = serializers.CharField(required=True)
	new_password = serializers.CharField(required=True,
										 validators=[validate_password])

	def create(self, validated_data):
		user = User.objects.get(username=validated_data['user'])
		current_password = validated_data['current_password']
		new_password = validated_data['new_password']
		if not user.check_password(current_password):
			raise ValidationError({'message': 'Старый пароль неверный'})
		if current_password == new_password:
			raise ValidationError(
				{'message': 'Новый пароль должен быть отличен от старого'})
		user.set_password(new_password)
		user.save()
		return user


class IngredientSerializer(serializers.ModelSerializer):
	class Meta:
		model = Ingredients
		fields = '__all__'

	extra_kwargs = {'id': {'required': True}}


class TegSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tegs
		fields = '__all__'

	extra_kwargs = {'id': {'required': True}}


class SubscriptionsSerializer(serializers.ModelSerializer):
	recipes = serializers.SerializerMethodField()
	recipes_count = serializers.SerializerMethodField()
	is_subscribed = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = (
			'email', 'id', 'username', 'first_name',
			'last_name', 'is_subscribed', 'recipes',
			'recipes_count')
		read_only_fields = ('email', 'username')

	def get_recipes(self, obj):
		recepies = Recipes.objects.filter(author=obj)
		serializer = RecipFavorite(recepies, many=True)
		return serializer.data

	def get_recipes_count(self, obj):
		return len(Recipes.objects.filter(author=obj))

	def get_is_subscribed(self, obj):
		request_user = self.context.get('request_user', None).id
		users = Follow.objects.filter(author=obj, user=request_user).exists()
		return users

	def validate(self, data):
		author = self.instance
		user = self.context.get('request').user
		if Follow.objects.filter(author=author, user=user).exists():
			raise ValidationError(
				detail='Вы уже подписаны на этого пользователя',
				code=400
			)
		elif user == author:
			raise ValidationError(
				detail='Нельзя подписаться на самого себя',
				code=400
			)
		return data


class IngredientAmmountSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(write_only=True)

	class Meta:
		model = IngredientAmmount
		fields = ('id', 'ammount')


class RecipesSerializer(serializers.ModelSerializer):
	author = UserSerializer()
	tags = TegSerializer(many=True)
	ingredients = serializers.SerializerMethodField()
	is_favorited = serializers.SerializerMethodField()
	is_in_shopping_cart = serializers.SerializerMethodField()
	image = Base64ImageField()

	class Meta:
		model = Recipes
		fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
				  'is_in_shopping_cart', 'name', 'image', 'text',
				  'cooking_time')

	def get_ingredients(self, obj):
		ingredients = obj.ingredients.values('id', 'name', 'measurement_unit',
											 'ingredientammount__ammount')
		return ingredients

	def get_is_favorited(self, obj):
		if self.context['request_user'] == 'AnonymousUser':
			return False
		user = self.context['request_user'].id
		return Favorite.objects.filter(recipe=obj, user=user).exists()

	def get_is_in_shopping_cart(self, obj):
		if self.context['request_user'] == 'AnonymousUser':
			return False
		user = self.context['request_user'].id
		return ShoppingCart.objects.filter(recipe=obj, user=user).exists()


class RecipesCreatSerializer(serializers.ModelSerializer):
	ingredients = IngredientAmmountSerializer(many=True)
	author = UserSerializer(read_only=True)
	tags = PrimaryKeyRelatedField(many=True, queryset=Tegs.objects.all())
	image = Base64ImageField()

	class Meta:
		model = Recipes
		fields = (
			'id','tags','author','ingredients','name','image','text',
			'cooking_time',
		)

	def validate_ingredients(self, value):
		if not value:
			raise ValidationError({
				'ingredients': 'Нужен хотя бы один ингредиент'
			})
		ingredients_list = []
		for item in value:
			try:
				ingredient = Ingredients.objects.get(id=item['id'])
			except:
				raise ValidationError({
					'ingredients': 'Такого ингридиента не существует'
				})
			if ingredient in ingredients_list:
				raise ValidationError({
					'ingredients': 'Ингридиенты не могут повторяться'
				})
			ingredients_list.append(ingredient)
		return value

	def validate_tags(self, value):
		if not value:
			raise ValidationError({'tags': 'Нужно выбрать хотя бы один тег'})
		tags_list = []
		for tag in value:
			if tag in tags_list:
				raise ValidationError(
					{'tags': 'Теги не должны повторяться'})
			tags_list.append(tag)
		return value

	def create(self, validated_data):
		tags = validated_data.pop('tags')
		ingredients = validated_data.pop('ingredients')
		recipe = Recipes.objects.create(**validated_data)
		recipe.tags.set(tags)
		self.create_ingredients_amounts(recipe=recipe, ingredients=ingredients)
		return recipe

	def update(self, instance, validated_data):
		tags = validated_data['tags']
		ingredients = validated_data.pop('ingredients')
		instance = super().update(instance, validated_data)
		instance.tags.clear()
		instance.tags.set(tags)
		instance.ingredients.clear()
		self.create_ingredients_amounts(recipe=instance,
										ingredients=ingredients)
		instance.save()
		return instance

	def create_ingredients_amounts(self, ingredients, recipe):
		for ingredient in ingredients:
			IngredientAmmount.objects.create(
				ingredient=Ingredients.objects.get(id=ingredient['id']),
				recipes=recipe,
				ammount=ingredient['ammount']
			)

	def to_representation(self, instance):
		context = {'request_user': self.context.get('request_user')}
		return RecipesSerializer(instance, context=context).data


class RecipFavorite(serializers.ModelSerializer):
	image = Base64ImageField()

	class Meta:
		model = Recipes
		fields = (
			'id',
			'name',
			'image',
			'cooking_time'
		)
