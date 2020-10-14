from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name="register"),
    path('login', views.login, name="login"),
    path('forgetPassword', views.forgetPassword, name="forgetPassword"),
    path('forgetPasswordValidation', views.forgetPasswordValidation, name="forgetPasswordValidation"),
    path('addNewGame', views.addNewGame, name="addNewGame"),
    path('addNewItem', views.addNewItem, name="addNewItem"),
    path('addGameReward', views.addGameReward, name="addGameReward"),
    path('removeGameReward', views.removeGameReward, name="removeGameReward"),
    path('clearGameReward', views.clearGameReward, name="clearGameReward"),
    path('addNewProbability', views.addNewProbability, name="addNewProbability"),
    path('updateProbability', views.updateProbability, name="updateProbability"),
    path('openTheBox', views.openTheBox, name="openTheBox"),
    path('editProfile', views.editProfile, name="editProfile"),
    path('changePassword', views.changePassword, name="changePassword"),
]
