from django.urls import path
from accounts import views as AccountViews
from . import views


urlpatterns = [
    path('', AccountViews.studentDashboard, name='student'),
    path('profile/', views.studentProfile, name='studentProfile'),
    path('my_orders/', views.my_orders, name='student_my_orders'),
    path('order_detail/<int:order_number>/', views.order_detail, name='order_detail'),
]