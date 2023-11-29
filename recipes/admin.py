from django.contrib import admin

from .models import (Favorite, IngredientAmmount, Ingredients, Recipes,
                     ShoppingCart, Tegs)

# Register your models here.
admin.site.register(Ingredients)
admin.site.register(Tegs)
admin.site.register(Recipes)
admin.site.register(IngredientAmmount)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)