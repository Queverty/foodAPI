from rest_framework.permissions import BasePermission

from recipes.models import Recipes


class UpdateDataPermission(BasePermission):

	def has_permission(self, request, view, *args, **kwargs):
		recipe_author = Recipes.objects.get(id=view.kwargs['pk']).author
		if request.user == recipe_author or request.user.is_superuser or request.user.is_staff:
			return True
		return False
