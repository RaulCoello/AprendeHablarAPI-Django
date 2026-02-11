from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Game,Question,Answer
from django.http import JsonResponse
from django.core.files.storage import default_storage
from .utils.face_detector import detectar_rostros
from .utils.tts_service import generate_game_tts
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
				'image':g.image.url if g.image else None,
				'titulo_tts': g.titulo_tts.url if g.titulo_tts else None
			}
			return JsonResponse(data)
		except Game.DoesNotExist:
		 	return JsonResponse({'error':'Game no existe con id'}, status=404)


	# Post para crear
	if request.method == 'POST' and id is None:
		title = request.POST.get('title')
		color = request.POST.get('color', '')
		image = request.FILES.get('image')  # viene de FormData
		titulo_tts = ""
		#data = json.loads(request.body)

		# generar tts si no viene vacio el texto
		if title.strip():
			#crear carpeta para almacenar temporalmente el tss_game
			tss_dir = os.path.join(settings.MEDIA_ROOT, "tmp/tss/game")
			ruta_tts = generate_game_tts(f"Vas a jugar el juego {title}", tss_dir, "game")

			# Rutas absolutas
			temp_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_tts)

			# Crear nombre definitivo
			filename = os.path.basename(ruta_tts)
			final_rel_path = f"tss/game/{filename}"
			final_abs_path = os.path.join(settings.MEDIA_ROOT, final_rel_path)

			# Mover archivo tmp → tss
			os.makedirs(os.path.dirname(final_abs_path), exist_ok=True)
			shutil.move(temp_abs_path, final_abs_path)

			#print(final_rel_path) --> este de aqui guardar en el objeto
			#g.titulo_tts = final_rel_path 

			titulo_tts = final_rel_path 


		g = Game.objects.create(
			title = title,
			color = color,
			image = image,
			titulo_tts = titulo_tts
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
			
			tss_anterior = g.titulo_tts.url if g.titulo_tts else None
			
			g.title = title
			g.color = color

			if image:
				# opcional: borrar imagen anterior
				#if g.image:
					#g.image.delete(save=False)
				g.image = image

			#crear el tts
			if title.strip():

				#crear carpeta para almacenar temporalmente el tss_game
				tss_dir = os.path.join(settings.MEDIA_ROOT, "tmp/tss/game")

				ruta_tts = generate_game_tts(f"Vas a jugar el juego {title}", tss_dir, "game")
				#print(f"Guardado en: {ruta_tts}") 

				# ahora mover el archivo de esa ruta ajaj skere mod diablo
				# ejemplo: tmp/tss/game/56f75474f96e4ed69bc3985d68c89000.wav

    			# Rutas absolutas
				temp_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_tts)

    			# Crear nombre definitivo
				filename = os.path.basename(ruta_tts)
				final_rel_path = f"tss/game/{filename}"
				final_abs_path = os.path.join(settings.MEDIA_ROOT, final_rel_path)

    			# Mover archivo tmp → tss
				os.makedirs(os.path.dirname(final_abs_path), exist_ok=True)
				shutil.move(temp_abs_path, final_abs_path)

			
				#print(final_rel_path) --> este de aqui guardar en el objeto
				g.titulo_tts = final_rel_path 
				
				# eliminar el anterior jajaj skere modo diablito
				# si existe viene en esta forma: /media/tss/game/fcb7bcab4f7442feb670ac0833698d3c.wav
				
				if tss_anterior:
					ruta_delete = tss_anterior.replace("/media/", "")
					delete_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_delete)

					if os.path.exists(delete_abs_path):
						os.remove(delete_abs_path)



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
				'number_question':q.number_question,
				'title_tts':q.title_tts.url if q.title_tts else None,
				'indication_tts':q.indication_tts.url if q.indication_tts else None

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
		title_tts= ""
		indication_tts =""
		

		# aqui agregar el tss cuando se crea ajajaj skere
		#crear el tss del title
		if title.strip():
				
			tss_dir = os.path.join(settings.MEDIA_ROOT, "tmp/tss/question")
			ruta_tts = generate_game_tts(f"{title}", tss_dir, "question")
				
			temp_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_tts)
			filename = os.path.basename(ruta_tts)
				
			final_rel_path = f"tss/question/{filename}"
			final_abs_path = os.path.join(settings.MEDIA_ROOT, final_rel_path)
				
			os.makedirs(os.path.dirname(final_abs_path), exist_ok=True)
			shutil.move(temp_abs_path, final_abs_path)
				
			title_tts = final_rel_path 

		#crear el tss de la indicacion
		if indication.strip():
			tss_dir = os.path.join(settings.MEDIA_ROOT, "tmp/tss/question")
			ruta_tts = generate_game_tts(f"{indication}", tss_dir, "question")
				
			temp_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_tts)
			filename = os.path.basename(ruta_tts)
				
			final_rel_path = f"tss/question/{filename}"
			final_abs_path = os.path.join(settings.MEDIA_ROOT, final_rel_path)
				
			os.makedirs(os.path.dirname(final_abs_path), exist_ok=True)
			shutil.move(temp_abs_path, final_abs_path)
				
			indication_tts = final_rel_path 

		
		g = Question.objects.create(
			title = title,
			indication = indication,
			resource = image,
			type_question = type_question,
			type_resource = type_resource,
			number_question = number_question,
			game_id =game_id,
			title_tts = title_tts,
			indication_tts = indication_tts
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

			tss_anterior = g.title_tts.url if g.title_tts else None
			tss_anterior_indicacion = g.indication_tts.url if g.indication_tts else None

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


			#crear el tss del title
			if title.strip():
				
				tss_dir = os.path.join(settings.MEDIA_ROOT, "tmp/tss/question")
				ruta_tts = generate_game_tts(f"{title}", tss_dir, "question")
				
				temp_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_tts)
				filename = os.path.basename(ruta_tts)
				
				final_rel_path = f"tss/question/{filename}"
				final_abs_path = os.path.join(settings.MEDIA_ROOT, final_rel_path)
				
				os.makedirs(os.path.dirname(final_abs_path), exist_ok=True)
				shutil.move(temp_abs_path, final_abs_path)
				
				g.title_tts = final_rel_path 
				
				if tss_anterior:
					ruta_delete = tss_anterior.replace("/media/", "")
					delete_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_delete)
				
					if os.path.exists(delete_abs_path):
						os.remove(delete_abs_path)

			
			#crear el tss de la indicacion
			if indication.strip():
				tss_dir = os.path.join(settings.MEDIA_ROOT, "tmp/tss/question")
				ruta_tts = generate_game_tts(f"{indication}", tss_dir, "question")
				
				temp_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_tts)
				filename = os.path.basename(ruta_tts)
				
				final_rel_path = f"tss/question/{filename}"
				final_abs_path = os.path.join(settings.MEDIA_ROOT, final_rel_path)
				
				os.makedirs(os.path.dirname(final_abs_path), exist_ok=True)
				shutil.move(temp_abs_path, final_abs_path)
				
				g.indication_tts = final_rel_path 
				
				if tss_anterior_indicacion:
					ruta_delete = tss_anterior_indicacion.replace("/media/", "")
					delete_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_delete)
				
					if os.path.exists(delete_abs_path):
						os.remove(delete_abs_path)



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

	# Get con el id de la answer
	if request.method == 'GET' and id is not None:
		try:
			q = Answer.objects.get(id=id)
			data = {
				'id':q.id,
				'answer':q.answer,
				'color':q.color,
				'is_correct':q.is_correct,
				'sound':q.sound.url if q.sound else None,
				'number_answer':q.number_answer,
				'answer_image':q.answer_image.url if q.answer_image else None,
				'question_id':q.question_id,
				'answer_tts':q.answer_tts.url if q.answer_tts else None
			}
			return JsonResponse(data)
		except Question.DoesNotExist:
			return JsonResponse({'error':'Answer no existe id'}, status= 404)



	#Post para crear answers
	if request.method == 'POST' and id is None:
		answer = request.POST.get('text', '')
		color = request.POST.get('color', '')
		is_correct = request.POST.get('correct', '')
		sound = request.FILES.get('sound', '')
		number_answer = request.POST.get('number_answer', 1)
		answer_image = request.FILES.get('answer_image', '')
		question_id = request.POST.get('question_id')
		answer_tts = ""


		# aqui crear el tss
		if answer.strip():

			#crear carpeta para almacenar temporalmente el tss_game
			tss_dir = os.path.join(settings.MEDIA_ROOT, "tmp/tss/answer")

			ruta_tts = generate_game_tts(f"{answer}", tss_dir, "answer")
			

			# ahora mover el archivo de esa ruta ajaj skere mod diablo
			# ejemplo: tmp/tss/game/56f75474f96e4ed69bc3985d68c89000.wav

    		# Rutas absolutas
			temp_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_tts)

    		# Crear nombre definitivo
			filename = os.path.basename(ruta_tts)
			final_rel_path = f"tss/answer/{filename}"
			final_abs_path = os.path.join(settings.MEDIA_ROOT, final_rel_path)

    		# Mover archivo tmp → tss
			os.makedirs(os.path.dirname(final_abs_path), exist_ok=True)
			shutil.move(temp_abs_path, final_abs_path)

			
			#print(final_rel_path) --> este de aqui guardar en el objeto
			answer_tts = final_rel_path 


		a = Answer.objects.create(
			answer = answer,
			color = color,
			is_correct = is_correct,
			sound = sound,
			number_answer = number_answer,
			answer_image =answer_image,
			question_id= question_id,
			answer_tts = answer_tts
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

			tss_anterior= a.answer_tts.url if a.answer_tts else None

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


			# aqui agregar el tts
			# answer_tts
            #crear el tts
			if answer.strip():

				#crear carpeta para almacenar temporalmente el tss_game
				tss_dir = os.path.join(settings.MEDIA_ROOT, "tmp/tss/answer")

				ruta_tts = generate_game_tts(f"{answer}", tss_dir, "answer")
				#print(f"Guardado en: {ruta_tts}") 

				# ahora mover el archivo de esa ruta ajaj skere mod diablo
				# ejemplo: tmp/tss/game/56f75474f96e4ed69bc3985d68c89000.wav

    			# Rutas absolutas
				temp_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_tts)

    			# Crear nombre definitivo
				filename = os.path.basename(ruta_tts)
				final_rel_path = f"tss/answer/{filename}"
				final_abs_path = os.path.join(settings.MEDIA_ROOT, final_rel_path)

    			# Mover archivo tmp → tss
				os.makedirs(os.path.dirname(final_abs_path), exist_ok=True)
				shutil.move(temp_abs_path, final_abs_path)

			
				#print(final_rel_path) --> este de aqui guardar en el objeto
				a.answer_tts = final_rel_path 
				
				# eliminar el anterior jajaj skere modo diablito
				# si existe viene en esta forma: /media/tss/game/fcb7bcab4f7442feb670ac0833698d3c.wav
				
				if tss_anterior:
					ruta_delete = tss_anterior.replace("/media/", "")
					delete_abs_path = os.path.join(settings.MEDIA_ROOT, ruta_delete)

					if os.path.exists(delete_abs_path):
						os.remove(delete_abs_path)



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

