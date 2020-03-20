from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from django.http import JsonResponse
from django.core.cache import cache
from .scraper import *

'''
    We scrap results every 1800seconds since they are not updated every second.

'''

# Create your views here.
def index(request):
    try:
        #get table of all countries from cache, or scrap it
        response = cache.get('table', False)        
        if not(response):
            response = get_table()
            cache.set("table", response, 1800)
            
            #check if  list of countries is in cache, put it otherwise
            countries = cache.get('countries', False)
            if not(countries):
                countries =  list(response.keys())
                cache.set("countries", countries, None)
            
            #put details of every country in cache
            for i in countries:
                cache.set("cached_"+i, response[i], 1800)
        
        return JsonResponse(response)
    except Exception as err:
        return JsonResponse({'erreur': str(err)})

def country_detail(request, name):
    try:
        name = str(name).lower()

        #get list of countries from cache, or scrap it
        countries = cache.get('countries', False)

        #check if the given name is valid
        if countries != False and name not in countries:
            return JsonResponse({'error': 'The specified country is not valid.'})
        
        #get table of all countries from cache, or scrap it
        table = cache.get('table', False)   
        if not(table):
            table = get_table()
            cache.set("table", table, 1800)

        if not(countries):
            countries = list(table.keys())
            cache.set("countries", countries, None)
        
        #check if the given name is valid
        if name not in countries:
            return JsonResponse({'error': 'The specified country is not valid.'})

        #if so, get results from cache or scrap them
        response = cache.get('cached_'+str(name) , False)

        if not(response):
            table = get_table()[str(name)]
            cache.set("cached_"+str(name), table, 1800)
            response = table
        
        #we return the result as a json object
        return JsonResponse(response)

    except Exception as err:
        return JsonResponse({'Internal Server Error': str(err)})

def detail(request, country_id):
    try:
        response = cache.get('cached_'+str(country_id), False)

        if not(response):
            response = get_data(country_id)
            cache.set("cached_"+str(country_id), response, 60)

        
        return JsonResponse(response)
    except Exception as err:
        return JsonResponse({'erreur': str(err)})