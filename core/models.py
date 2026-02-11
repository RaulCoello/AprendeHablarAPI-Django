from django.db import models




# ==============================
# Funciones dinámicas de rutas
# ==============================

def game_tts_path(instance, filename):
    return f"tts/games/game_{instance.id}.wav"


def question_title_tts_path(instance, filename):
    return f"tts/questions/question_{instance.id}_title.wav"


def question_indication_tts_path(instance, filename):
    return f"tts/questions/question_{instance.id}_indication.wav"


def answer_tts_path(instance, filename):
    return f"tts/answers/answer_{instance.id}.wav"




# Create your models here.

# clase para los juegos
class Game(models.Model):
	title = models.CharField(max_length=150)
	color = models.CharField(max_length=50)
	image = models.ImageField(upload_to='images/', blank=True, null=True)
	# agregar aqui un nuevo campo para almacenar un tts que diga "Vas a jugar el juego [title]"

	titulo_tts = models.FileField(
        upload_to=game_tts_path,
        blank=True,
        null=True
    )

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
	# agregar aqui dos campos para almacenar tts
	# uno que indique la pregunta [title]
	title_tts = models.FileField(
        upload_to=question_title_tts_path,
        blank=True,
        null=True
    )
	# uno que indique [indication]
	indication_tts = models.FileField(
        upload_to=question_indication_tts_path,
        blank=True,
        null=True
    )

	def __str__(self):
		return self.title


class Answer(models.Model):
	answer = models.CharField(max_length=150)
	color = models.CharField(max_length=50)
	is_correct = models.BooleanField(default=False)
	sound = models.FileField(upload_to='sounds/', blank=True, null=True)
	number_answer = models.IntegerField()
	answer_image = models.ImageField(upload_to='images/', blank=True, null=True)
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
	# agregar aqui un campo para almacenar el tts que indique [answer]
	answer_tts = models.FileField(
        upload_to=answer_tts_path,
        blank=True,
        null=True
    )
    
	def __str__(self):
		return self.answer