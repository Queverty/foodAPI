from django import forms
from django.shortcuts import get_object_or_404
from service_objects.services import Service

from api.services.base.get_model import get_model
from recipes.models import Ingredients


class IngredientGetService(Service):
	id = forms.IntegerField()

	def process(self):
		return get_object_or_404(Ingredients, id=self.cleaned_data['id'])
