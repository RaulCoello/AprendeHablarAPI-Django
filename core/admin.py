from django.contrib import admin
from .models import Game,Question,Answer

# Register your models here.
admin.site.register(Game)
admin.site.register(Question)
admin.site.register(Answer)