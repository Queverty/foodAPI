from django import forms
from django.shortcuts import get_object_or_404
from service_objects.services import Service

from api.services.base.get_model import get_model
from recipes.models import Tegs


class TegGetService(Service):
	id = forms.IntegerField()

	def process(self):
		return get_object_or_404(Tegs,id=self.cleaned_data['id'])
