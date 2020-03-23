from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from django.http import JsonResponse
from django.core.cache import cache
from .scraper import *
import threading


'''
    We scrap results every 1800seconds since they are not updated every second.

'''
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate', 
            'Accept': '*/*', 
            'Referer':"http://www.google.co.ma",
            'Connection': 'close'}
    

COUNTRY_ERROR = {'error': 'The specified country is not valid.'}
SERVER_ERROR = {'error': 'INTERNAL SERVER ERROR, try again later.'}

def update_regions_morocco():
    regions = get_regions_morocco(headers)
    cache.set("morocco_regions", regions, 1800)

def thread_update_regions():
    saver = threading.Thread(target=update_regions_morocco)
    saver.start()

    

def save_countries_to_cache(table, countries):
    for country in countries:
        cache.set("cached"+country, table[country], 1800)

def thread_save_countries(table, countries):
    saver = threading.Thread(target=save_countries_to_cache, args=(table, countries))
    saver.start()


# Return list of available countries
def countries(request):
    try:
        #get table of all countries from cache, or scrap it
        countries = cache.get('countries', False)        
        if not(countries):
            table = get_table()
            countries = list(table.keys())
            cache.set("countries", countries, None)
            
            #start another thread to save all countries
            thread_save_countries(table, countries)
        
        return JsonResponse({'list':countries})
    except Exception as err:
        return JsonResponse({'a': SERVER_ERROR, 'error':str(err)})

def country_detail(request, name):
    try:
        name = str(name).lower().replace(' ','').replace('%20','')
        #IF list of countries in cache, check if name is valide
        countries = cache.get('countries', False)        
        if countries != False and name not in countries:
            return JsonResponse(COUNTRY_ERROR)

        #if list not in cache, we check directly for name in cache
        #if response already in cache, return it
        response = cache.get('cached'+str(name), False)
        if response != False:
            return JsonResponse(response)
        
        #else, extract all countries, save them in cache, and send corresponding country.
        #a key error will send COUNTRYERROR if name not valide and country list not in cache
        else:
            table = get_table()
            countries = list(table.keys())
            cache.set("countries", countries, None)

            #start another thread to save all countries
            thread_save_countries(table, countries)
            
            if name == 'morocco':
                thread_update_regions()

            response = table[name]
            return JsonResponse(response)
            
    
    except KeyError as err:
        return JsonResponse(COUNTRY_ERROR)
    except Exception as err:
        return JsonResponse({'Internal Server Error': str(err)})

def regions(request):

    try: 
        regions = cache.get('morocco_regions', False)   
             
        if not(regions) or 'error' in list(regions.keys()):
            regions = get_regions_morocco(headers)
            cache.set("morocco_regions", regions, 1800)
            
        
        return JsonResponse(regions)
    except Exception as err:
        SERVER_ERROR['error']= str(err)
        return JsonResponse(SERVER_ERROR)

def index(request):
    return render(request, 'stats/index.html')