from django.contrib import admin
from .models import Character, Question, Answer, Item


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text",)
    inlines = [AnswerInline]


admin.site.register(Character)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Item)
