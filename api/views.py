from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Favorite, Recipes, ShoppingCart
from user.models import Follow, User

from .permissions import UpdateDataPermission
from .serializers import (ChangePasswordSerializer, IngredientSerializer,
						  RecipesCreatSerializer, RecipesSerializer,
						  RecipFavorite, SubscriptionsSerializer,
						  TegSerializer, UserRegistrationSerializer,
						  UserSerializer)
from .services.ingredients.get_by_id import IngredientGetService
from .services.ingredients.list import IngredientsListService
from .services.tegs.get_by_id import TegGetService
from .services.tegs.list import TegsListService


# Create your views here.

class UsersViewSet(viewsets.ViewSet):

	def get_permissions(self):
		if self.action in ['retrieve', 'current_user', 'subscribe',
						   'subscriptions', 'set_password']:
			return [IsAuthenticated(), ]
		return [AllowAny(), ]

	def list(self, request):
		outcome = User.objects.all()
		serializer = UserSerializer(outcome, many=True, context={
			'request': request
		})
		return Response({'count': len(outcome),
						 "next": 'http://foodgram.example.org/api/users/?page=4',
						 "previous": 'http://foodgram.example.org/api/users/?page=2',
						 'results': serializer.data})

	def retrieve(self, request, *args, **kwargs):
		user_info = get_object_or_404(User.objects.all(), id=kwargs['pk'])
		serializer = UserSerializer(user_info,
									context={'request_user': request.user})
		return Response(serializer.data)

	@action(detail=False, methods=['get'])
	def me(self, request):
		outcome = User.objects.get(username=request.user)
		serializer = UserSerializer(outcome,
									context={'request_user': request.user})
		return Response(serializer.data)

	def create(self, request, *args, **kwargs):
		serializer = UserRegistrationSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)

	@action(detail=False, methods=['post'])
	def set_password(self, request, *args, **kwargs):
		serializer = ChangePasswordSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.validated_data['user'] = request.user
		serializer.save()
		return Response({'message': 'Пароль успешно изменен'})

	@action(detail=False, methods=['get'])
	def subscriptions(self, request, *args, **kwargs):
		user = User.objects.filter(following__user=request.user)
		serializer = SubscriptionsSerializer(user, many=True,
											 context={
												 'request_user': request.user})
		return Response({"count": len(user),
						 "next": "http://foodgram.example.org/api/users/subscriptions/?page=4",
						 "previous": "http://foodgram.example.org/api/users/subscriptions/?page=2",
						 'results': serializer.data})

	@action(detail=True, methods=['post', 'delete'])
	def subscribe(self, request, pk=None, *args, **kwargs):
		follower = get_object_or_404(User.objects.all(),
									 id=pk)
		if request.method == "POST":
			serializer = SubscriptionsSerializer(follower,
												 context={
													 'request_user': request.user},
												 data=request.data)
			serializer.is_valid(raise_exception=True)
			serializer.validated_data['follower'] = follower
			Follow.objects.create(user=request.user, author=follower)
			return Response(serializer.data, status=201)
		else:
			try:
				subscribe_last = get_object_or_404(Follow.objects.all(),
												   user=request.user,
												   author=follower)
				subscribe_last.delete()
			except Exception:
				return Response({'errors':
									 "Вы не подписаны на пользователя"},
								status=400)
		return Response(status=204)


class IngredientsListAPIView(APIView):

	def get(self, request, *args, **kwargs):
		outcome = IngredientsListService.execute({})
		return Response(outcome.values().reverse())


class IngredientGetAPIView(APIView):

	def get(self, request, *args, **kwargs):
		outcome = IngredientGetService.execute({'id': kwargs['pk']})
		return Response(IngredientSerializer(outcome).data)


class TegsListAPIView(APIView):

	def get(self, request, *args, **kwargs):
		outcome = TegsListService.execute({})
		return Response(outcome.values().reverse())


class TegGetAPIView(APIView):

	def get(self, request, *args, **kwargs):
		outcome = TegGetService.execute({'id': kwargs['pk']})
		return Response(TegSerializer(outcome).data)


class RecipesViewSet(viewsets.ViewSet):

	def get_permissions(self):
		if self.action in ['partial_update', 'destroy']:
			return [IsAuthenticated(), UpdateDataPermission(), ]
		elif self.action in ['favorite', 'create', 'shopping_cart',
							 'download_shopping_cart']:
			return [IsAuthenticated(), ]
		return [AllowAny(), ]

	def list(self, request, *args, **kwargs):
		outcome = Recipes.objects.all()
		serializer = RecipesSerializer(outcome, many=True,
									   context={
										   'request_user': request.user}, )
		return Response({'count': len(outcome),
						 "next": "http://foodgram.example.org/api/recipes/?page=4",
						 "previous": "http://foodgram.example.org/api/recipes/?page=2",
						 'results': serializer.data})

	def create(self, request, *args, **kwargs):
		serializer = RecipesCreatSerializer(data=request.data,
											context={
												'request_user': request.user,
												'request': request})
		serializer.is_valid(raise_exception=True)
		serializer.validated_data['author'] = request.user
		serializer.save()
		return Response(serializer.data)

	def retrieve(self, request, *args, **kwargs):
		recipes_info = get_object_or_404(Recipes.objects.all(),
										 id=kwargs['pk'])
		serializer = RecipesSerializer(recipes_info,
									   context={'request_user': request.user})
		return Response(serializer.data)

	def partial_update(self, request, pk=None):
		recipes_info = get_object_or_404(Recipes, id=pk)
		serializer = RecipesCreatSerializer(recipes_info, data=request.data,
											partial=True,
											context={
												'request_user': request.user})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)

	def destroy(self, request, pk=None):
		recipes = get_object_or_404(Recipes, id=pk)
		recipes.delete()
		return Response(status=204)

	@action(detail=True, methods=['post', 'delete'])
	def favorite(self, request, pk=None, *args, **kwargs):
		recipe = get_object_or_404(Recipes, id=pk)
		if request.method == 'POST':
			if Favorite.objects.filter(user=request.user.id,
									   recipe=recipe).exists():
				return Response({'errors': 'Рецепт уже в избранном'},
								status=400)
			Favorite.objects.create(user=request.user, recipe=recipe)
			serializer = RecipFavorite(recipe)
			return Response(serializer.data)
		else:
			try:
				favorite = get_object_or_404(Favorite.objects.all(),
											 user=request.user,
											 recipe=recipe)
				favorite.delete()
			except Exception as error:
				return Response({'errors': "Рецепт уже удален"}, status=400)
			return Response(status=204)

	@action(detail=True, methods=['post', 'delete'])
	def shopping_cart(self, request, pk=None, *args, **kwargs):
		recipe = get_object_or_404(Recipes, id=pk)
		if request.method == 'POST':
			if ShoppingCart.objects.filter(user=request.user,
										   recipe=recipe).exists():
				return Response({'errors': 'Рецепт уже добавлен в корзину'},
								status=400)
			ShoppingCart.objects.create(user=request.user, recipe=recipe)
			serializer = RecipFavorite(recipe)
			return Response(serializer.data)
		else:
			try:
				shoppingcart = get_object_or_404(
					ShoppingCart.objects.all(),
					user=request.user,
					recipe=recipe)
				shoppingcart.delete()
			except Exception:
				return Response({'errors': 'Рецепт уже удален'}, status=400)
			return Response(status=204)

	@action(detail=False, methods=['get'], )
	def download_shopping_cart(self, request, *args, **kwargs):
		data = ShoppingCart.objects.filter(user=request.user)
		response = HttpResponse(content_type='text/plain')
		response['Content-Disposition'] = 'attachment; filename="data.txt"'
		for info in data:
			response.write(f'\n{info}')
		return response
