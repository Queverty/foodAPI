from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
	email = models.EmailField(max_length=254, unique=True)

	def __str__(self):
		return self.username


class Follow(models.Model):
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="follower",
		verbose_name="Подписчик",
	)
	author = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="following",
		verbose_name="Автор",
	)

	def __str__(self):
		return f"Подписчик {self.user} - автор {self.author}"

	class Meta:
		verbose_name = 'Подписка'
		verbose_name_plural = 'Подписки'