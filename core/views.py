from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Game,Question,Answer
from django.http import JsonResponse
from django.core.files.storage import default_storage
from .utils.face_detector import detectar_rostros
from django.conf import settings
import json
import os
import shutil


# Create your views here.

# API
# Juegos

@csrf_exempt
def Games(request, id=None):

	# Get all
	if request.method =='GET' and id is None:
		games = list(Game.objects.values())
		return JsonResponse(games, safe=False)

	# Get con id 
	if request.method == 'GET' and id is not None:
		try:
			g = Game.objects.get(id=id)
			data = {
				'id':g.id,
				'title':g.title,
				'color':g.color,
				'image':g.image
			}
			return JsonResponse(data)
		except Game.DoesNotExist:
		 	return JsonResponse({'error':'Game no existe con id'}, status=404)


	# Post para crear
	if request.method == 'POST' and id is None:
		title = request.POST.get('title')
		color = request.POST.get('color', '')
		image = request.FILES.get('image')  # viene de FormData

		#data = json.loads(request.body)
		
		g = Game.objects.create(
			title = title,
			color = color,
			image = image
			)
		return JsonResponse({'id':g.id,'title':g.title,'image': g.image.url if g.image else None})	 


	# Put => Post Logico para editar un juego
	if request.method == 'POST' and id is not None:
		try:
			g = Game.objects.get(id=id)
			#data = json.loads(request.body)

			title = request.POST.get('title', g.title)
			color = request.POST.get('color', g.color)
			image = request.FILES.get('image')

			g.title = title
			g.color = color

			if image:
				# opcional: borrar imagen anterior
				#if g.image:
					#g.image.delete(save=False)
				g.image = image

			g.save()

			return JsonResponse({'mensaje':'Game actualizado'})

		except Game.DoesNotExist:
			return JsonResponse({'error':'Game no existe id'}, status=404)

	# Delete
	if request.method ==  'DELETE' and id is not None:
		try:
			g = Game.objects.get(id=id)
			g.delete()
			return JsonResponse({'mensaje':'Game eliminado'})
		except Game.DoesNotExist:
			return JsonResponse({'error':'Game no existe'},status=404)
	 


	#retornar por defecto 
	return JsonResponse({'mensaje':'Metodo no permitido'},status=405)


# Preguntas 
@csrf_exempt
def Questions(request, id=None):

	#Get all
	if request.method == 'GET' and id is None:
		questions = list(Question.objects.values())
		return JsonResponse(questions, safe=False)

	# Get con el id del juego
	if request.method == 'GET' and id is not None:
		try:
			q = Question.objects.get(id=id)
			data = {
				'id':q.id,
				'title':q.title,
				'indication':q.indication,
				'resource':q.resource.url if q.resource else None,
				'type_question':q.type_question,
				'type_resource':q.type_resource,
				'number_question':q.number_question
			}
			return JsonResponse(data)
		except Question.DoesNotExist:
			return JsonResponse({'error':'Question no existe id'}, status= 404)

	# Post para crear una pregunta
	if request.method == 'POST' and id is None:
		title = request.POST.get('title')
		indication = request.POST.get('indication', '')
		type_question = request.POST.get('type_question', '')
		type_resource = request.POST.get('type_resource', '')
		number_question = request.POST.get('number_question', '')
		game_id = request.POST.get('game_id', '')
		image = request.FILES.get('image')  # viene de FormData

		
		g = Question.objects.create(
			title = title,
			indication = indication,
			resource = image,
			type_question = type_question,
			type_resource = type_resource,
			number_question = number_question,
			game_id =game_id 
			)
		return JsonResponse({'id':g.id,'title':g.title,'image': g.resource.url if g.resource else None})	 

	# Put => POST logico para actualizar 
	if request.method == 'POST' and id is not None:
		try:
			g = Question.objects.get(id=id)
			#data = json.loads(request.body)

			title = request.POST.get('title', g.title)
			indication = request.POST.get('indication', g.indication)
			type_question = request.POST.get('type_question', g.type_question)
			type_resource = request.POST.get('type_resource', g.type_resource)
			number_question = request.POST.get('number_question', g.number_question)
			game_id = request.POST.get('game_id', g.game_id)
			image = request.FILES.get('image') # viene de FormData

			# reemplazar valores del registro
			g.title = title
			g.indication = indication
			g.type_question = type_question
			g.type_resource = type_resource
			g.number_question = number_question
			g.game_id = game_id

			if image:
				# opcional: borrar imagen anterior
				#if g.image:
					#g.image.delete(save=False)
				g.resource = image

			g.save()

			return JsonResponse({'mensaje':'Question actualizado'})

		except Game.DoesNotExist:
			return JsonResponse({'error':'Game no existe id'}, status=404)


	# Delete
	if request.method == 'DELETE' and id is not None:
		try:
			q = Question.objects.get(id=id)
			q.delete()
			return JsonResponse({'mensaje':'Question eliminado'})
		except Question.DoesNotExist:
			return JsonResponse({'error':'Question no existe id'}, status=404)

			
	#retornar por defecto 
	return JsonResponse({'mensaje':'Metodo no permitido'},status=405)


# Questions de Games
@csrf_exempt
def GamesQuestions(request, id=None):

	# Get all con id del game 
	if request.method == 'GET' and id is not None:
		questions_answers = list(Question.objects.filter(game_id=id).select_related('game','questions').values())
		return JsonResponse(questions_answers, safe = False)


# Answers 
@csrf_exempt
def Answers(request, id=None):

	# Get all 
	if request.method == 'GET' and id is None:
		answers = list(Answer.objects.values())
		return JsonResponse(answers, safe=False)


	#Post para crear answers
	if request.method == 'POST' and id is None:
		answer = request.POST.get('text', '')
		color = request.POST.get('color', '')
		is_correct = request.POST.get('correct', '')
		sound = request.FILES.get('sound', '')
		number_answer = request.POST.get('number_answer', 1)
		answer_image = request.FILES.get('answer_image', '')
		question_id = request.POST.get('question_id')

		a = Answer.objects.create(
			answer = answer,
			color = color,
			is_correct = is_correct,
			sound = sound,
			number_answer = number_answer,
			answer_image =answer_image,
			question_id= question_id
			)
		return JsonResponse({'id':a.id,'answer':a.answer,'image': a.answer_image.url if a.answer_image else None})	 


	# Post Logico con id para editar la respuesta
	if request.method == 'POST' and id is not None:
		try:

			a = Answer.objects.get(id=id)

			answer = request.POST.get('answer', a.answer)
			color = request.POST.get('color', a.color)
			is_correct = request.POST.get('is_correct', a.is_correct)
			sound = request.FILES.get('sound', '')
			number_answer = request.POST.get('number_answer',a.number_answer)
			answer_image = request.FILES.get('answer_image','')
			question_id = request.POST.get('question_id',a.question_id)

			# Reemplazar valores

			a.answer = answer
			a.color= color
			a.is_correct = is_correct
			a.number_answer= number_answer
			a.question_id = question_id

			if sound:
				a.sound = sound

			if answer_image:
				a.answer_image = answer_image

			a.save()

			return JsonResponse({'mensaje':'Answer Actualizada'})
		except Answer.DoesNotExist:
			return JsonResponse({'error':'Answer no encontrada id'}, status=404)





	#retornar por defecto 
	return JsonResponse({'mensaje':'Metodo no permitido'},status=405)


# Questions Answers
@csrf_exempt
def QuestionAnswers(request, id=None):

	#Get por id de question
	if request.method == 'GET' and id is not None:
		answers_question = list(Answer.objects.filter(question_id=id).select_related('question','answers').values())
		return JsonResponse(answers_question, safe = False)


# Endpoint para el detector de rostros skere modo diablo
@csrf_exempt
def DetectFaces(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    image = request.FILES.get("image")
    if not image:
        return JsonResponse({"error": "Imagen requerida"}, status=400)

    # Guardar imagen original temporal
    temp_image_path = default_storage.save(
        f"tmp/originals/{image.name}", image
    )

    abs_image_path = os.path.join(settings.MEDIA_ROOT, temp_image_path)

    # Carpeta para rostros
    faces_dir = os.path.join(settings.MEDIA_ROOT, "tmp/faces")

    # Detectar rostros
    faces = detectar_rostros(
        image_path=abs_image_path,
        output_dir=faces_dir,
        padding=0.25
    )

    # Construir URLs públicas
    faces_urls = [
    	f"tmp/faces/{f}"
    	for f in faces
	]


    return JsonResponse({
        "faces_count": len(faces_urls),
        "faces": faces_urls
    })




 #View para guardar las respuestas de las faces detectadas
@csrf_exempt
def CreateAnswerFromTempFace(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    text = request.POST.get("text", "")
    color = request.POST.get("color", "")
    is_correct = request.POST.get('correct', '')
    number_answer = request.POST.get("number_answer", 1)
    question_id = request.POST.get("question_id")
    image_path = request.POST.get("image_path")  # ejemplo: tmp/faces/abc.jpg

    if not image_path:
        return JsonResponse({"error": "image_path requerido"}, status=400)

    #  Validación básica
    if not image_path.startswith("tmp/faces/"):
        return JsonResponse({"error": "Ruta inválida"}, status=400)

    # Rutas absolutas
    temp_abs_path = os.path.join(settings.MEDIA_ROOT, image_path)

    if not os.path.exists(temp_abs_path):
        return JsonResponse({"error": "Imagen no encontrada"}, status=404)

    # Crear nombre definitivo
    filename = os.path.basename(image_path)
    final_rel_path = f"images/{filename}"
    final_abs_path = os.path.join(settings.MEDIA_ROOT, final_rel_path)

    # Mover archivo tmp → images
    os.makedirs(os.path.dirname(final_abs_path), exist_ok=True)
    shutil.move(temp_abs_path, final_abs_path)

    # Crear Answer usando la ruta relativa
    a = Answer.objects.create(
        answer=text,
        color=color,
        is_correct=is_correct,
        number_answer=number_answer,
        answer_image=final_rel_path,
        question_id=question_id
    )

    return JsonResponse({
        "id": a.id,
        "answer": a.answer,
        "image": a.answer_image.url if a.answer_image else None
    })

