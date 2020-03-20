from django.urls import path

from . import views

urlpatterns = [
     path('coronavirus/<int:country_id>/', views.detail, name='detail'),
     path('coronavirus/countries/', views.index, name='countries'),
     
     path('coronavirus/<slug:name>/', views.country_detail, name='ml')
]