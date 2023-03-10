from django.urls import path
from . import views

urlpatterns = [
    path('map/', views.show_map, name='show_map')
]
