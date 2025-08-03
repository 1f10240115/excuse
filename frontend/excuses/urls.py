from django.urls import path
from . import views

app_name = 'excuses'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/excuses/', views.get_excuses, name='get_excuses'),
    path('api/excuses/<int:excuse_id>/', views.get_excuse, name='get_excuse'),
    path('api/excuses/create/', views.create_excuse, name='create_excuse'),
    path('api/categories/', views.get_categories, name='get_categories'),
    path('generate_excuse/', views.generate_excuse, name='generate_excuse'),
] 