from django.contrib import admin

from user.models import Follow, User

# Register your models here.


admin.site.register(User)
admin.site.register(Follow)