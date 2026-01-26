from django.db import models

# Create your models here.

# clase para los juegos
class Game(models.Model):
	title = models.CharField(max_length=150)
	color = models.CharField(max_length=50)
	image = models.ImageField(upload_to='images/', blank=True, null=True)

	def __str__(self):
		return self.title


class Question(models.Model):
	title = models.CharField(max_length=150)
	indication = models.TextField(blank=True)
	resource = models.ImageField(upload_to='images/', blank=True, null=True)
	type_question = models.CharField(max_length=100)
	type_resource = models.CharField(max_length=100)
	number_question = models.IntegerField()
	game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='questions')

	def __str__(self):
		return self.title


class Answer(models.Model):
	answer = models.CharField(max_length=150)
	color = models.CharField(max_length=50)
	is_correct = models.BooleanField(default=False)
	sound = models.TextField(blank=True)
	number_answer = models.IntegerField()
	answer_image = models.ImageField(upload_to='images/', blank=True, null=True)
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')

	def __str__(self):
		return self.answer