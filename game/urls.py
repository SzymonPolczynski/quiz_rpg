from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("quiz/", views.quiz_view, name="quiz"),
    path("choose_class/", views.choose_class_view, name="choose_class"),
    path("profile/", views.profile_view, name="profile"),
]
