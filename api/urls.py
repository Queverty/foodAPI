from django.urls import include, path
from rest_framework import routers

from .views import *

router = routers.SimpleRouter()
router.register(r'users', UsersViewSet, basename='User')
router.register(r'recipes', RecipesViewSet, basename='recipes')
urlpatterns = [
	path('', include(router.urls)),
	path('ingredients/', IngredientsListAPIView.as_view()),
	path('ingredients/<int:pk>/', IngredientGetAPIView.as_view()),
	path('tags/', TegsListAPIView.as_view()),
	path('tags/<int:pk>/', TegGetAPIView.as_view()),
	# path('users/subscriptions/', MysubScriptionsAPIView.as_view()),
	# path('recipes/{id}/favorite/', FavoriteAPIView.as_view()),

]
