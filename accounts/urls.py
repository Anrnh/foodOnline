from django.urls import path
from . import views

urlpatterns = [
#    path('', views.myAccount),
    path('registerUser/', views.registerUser, name='registerUser')

]