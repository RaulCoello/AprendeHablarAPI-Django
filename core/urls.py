from django.urls import path
from . import views

urlpatterns = [
	#API

	#Only Games
	path('api/games/',views.Games),
	path('api/games/<int:id>/',views.Games),

	#Only Questions
	path('api/questions/',views.Questions),
	path('api/questions/<int:id>/',views.Questions),

	# questions games
	path('api/games/<int:id>/questions/',views.GamesQuestions),

	#Only Answers 
	path('api/answers/',views.Answers),
	path('api/answers/<int:id>/',views.Answers),

	# Answers Question
	path('api/answers/<int:id>/question/',views.QuestionAnswers),

	#FaceDetection
	path('api/face/',views.DetectFaces),

	#CreateAnswerFromTempFace
	path('api/faceanswer/',views.CreateAnswerFromTempFace)
]