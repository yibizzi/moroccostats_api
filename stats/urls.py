from django.urls import path

from . import views

urlpatterns = [
     path('coronavirus/countries/<int:country_id>/', views.detail, name='detail'),

     path('coronavirus/countries/', views.countries, name='countries'),
     
     path('', views.index, name='indexpage'),
     
     path('coronavirus/countries/<slug:name>/', views.country_detail, name='detail_by_name'),
     
     path('coronavirus/countries/morocco/regions', views.regions, name='morocco_regions')
]