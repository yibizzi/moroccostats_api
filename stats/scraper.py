import requests
import urllib.request
from bs4 import BeautifulSoup
from time import time
import re, sys


column_heads = {"Country Other": "country", 
            "TotalCases": "totalcases",
            "NewCases": "newcases", 
            "TotalDeaths": "totaldeaths", 
            "NewDeaths": "newdeaths",
            "TotalRecovered": "recovered",
            "ActiveCases": "activecases",
            "Serious Critical": "seriouscases",
            "Tot\u00a0Cases/1M pop": "total_per_one_million",
            'Deaths/1M pop':'deaths_per_million',
            '1stcase':'1stcase'
}

attributes = [
    {'top' : 'Currently Infected Patients',
    'left': 'in Mild Condition',
    'right': 'Serious or Critical'},

    {'top' : 'Cases which had an outcome',
    'left': 'Recovered / Discharged',
    'right': 'Deaths'},

]


def get_table():
    
    url = "https://www.worldometers.info/coronavirus/"

    response = requests.get(url , headers={'Connection':'close'})
    response=response.text
    soup = BeautifulSoup(response, "html.parser")
    Soup = soup.select("table[id='main_table_countries_today']")[0]
    #scraping the 1st 3 numbers: Cases, deaths and recovered
    head = Soup.select("th")

    head = [i.text.replace(',', ' ') for i  in head]

    rows = Soup.select("tbody tr")
    table = dict()
    for i in range(len(rows)):
        country_row = rows[i]
        columns = [i.text.strip() or '0' for i in country_row.select('td')]
        
        element = dict()

        for j in range(len(columns)):
            try:
                element[ column_heads[head[j]] ] = columns[j].replace(',','')
            except Exception as err:
                try:
                    element[ head[j] ] = columns[j].replace(',','')
                except Exception as e:
                    print("Exception occured: " + str(e) )

        
        table[columns[1].lower().replace(':','').replace(' ','').replace('%20','')]  = element
            
    return table


def get_regions_morocco(heads):
    '''Scrap the official Covid-19 website in Morocco'''

    url = 'http://www.covidmaroc.ma/'
    
    response = requests.get(url , headers=heads)
    
    response=response.text
    err =  {'error': str(response)}

    soup = BeautifulSoup(response, "html.parser").select("table[class='ms-rteTable-6']") 
    try:
        Soup = soup[0]
    except:
        return err

    #scraping the 1st 3 numbers: Cases, deaths and recovered
    head = Soup.select("tr[class='ms-rteTableHeaderRow-6'] th")

    head = [re.sub('[^A-Za-z0-9]+', '', i.text) for i  in head] 

    rows = Soup.select("tr[class='ms-rteTableOddRow-6']") + Soup.select("tr[class='ms-rteTableEvenRow-6']")

    table = dict()
    for i in range(len(rows)):
        region_row = rows[i]
        region_name =  re.sub('[^A-Za-z0-9]+', '',region_row.select("th")[0].text)
        region_count = re.sub('[^A-Za-z0-9]+', '', region_row.select("td")[0].text.split('\\')[0])
        
        if region_name!='':
            table[region_name] = region_count
    return table
    