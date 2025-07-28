from django.contrib import admin
from .models import Character, Question, Answer, Item, Category, Quest, QuestProgress, Enemy


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text",)
    inlines = [AnswerInline]


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "required_correct_answers",
        "experience_reward",
        "gold_reward",
        "item_reward",
    )


@admin.register(QuestProgress)
class QuestProgressAdmin(admin.ModelAdmin):
    list_display = ("character", "quest", "correct_answers", "is_completed")


admin.site.register(Character)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Enemy)
