from service_objects.services import Service

from api.services.base.get_model import get_model
from recipes.models import Ingredients


class IngredientsListService(Service):

	def process(self):
		return get_model(Ingredients)