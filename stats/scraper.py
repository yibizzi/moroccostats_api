import requests
import urllib.request
from bs4 import BeautifulSoup
from time import time
import re
import logging
import http.client as http_client

Soup = ''

column_heads = {"Country Other": "country", 
            "TotalCases": "totalcases",
            "NewCases": "newcases", 
            "TotalDeaths": "totaldeaths", 
            "NewDeaths": "newdeaths",
            "TotalRecovered": "recovered",
            "ActiveCases": "activecases",
            "Serious Critical": "seriouscases",
            "Tot\u00a0Cases/1M pop": "total_per_one_million"
}

attributes = [
    {'top' : 'Currently Infected Patients',
    'left': 'in Mild Condition',
    'right': 'Serious or Critical'},

    {'top' : 'Cases which had an outcome',
    'left': 'Recovered / Discharged',
    'right': 'Deaths'},

]

countries_ids = {
    1: 'italy',
    2:'china', 
    3:'iran',
    4:'spain',
    5:'germany',
    6:'france',
    7:'us',
    8:'uk'
    }

Data = dict()

web_url = "https://www.worldometers.info/coronavirus/"


def get_data(country_id):
    global Soup

    url = web_url + "country/" + countries_ids[country_id]

    response = requests.get(url).text
    soup = BeautifulSoup(response, "html.parser")
    bSoup = soup.select("div[class='content-inner']")[0]

    #scraping the 1st 3 numbers: Cases, deaths and recovered
    Soup = bSoup.select("div[id='maincounter-wrap']")
    Total = dict()
    for i in range(len(Soup)):
        title = Soup[i].select("h1")[0].text.strip(":")
        number = Soup[i].select("div")[0].text.strip()
        Total[title] = number
    Data['total'] = Total



    #Scraping the next 2 columns
    Soup = bSoup.select("div[class='col-md-6']")
    for i in range(len(Soup)):
        title = Soup[i].findChild("span", {"class":"panel-title"}).text.strip()
        main_head = Soup[i].findChild("div", {"class":"number-table-main"}).text.strip()

        right_left =   Soup[i].findAll("span", {"class":"number-table"})
        
        right_head, left_head = '', ''
        
        for number in right_left:
            try:
                style = number['style']
            except:
                style=''
            if style in ('color:#8080FF', 'color:#8ACA2B'):
                left_head = number.text.strip()
            else:
                right_head = number.text.strip()

        Data[title] = {
            attributes[i]['top'] : main_head,
            attributes[i]['right'] : right_head,
            attributes[i]['left'] : left_head            
        }

    Data['country'] = countries_ids[country_id]
    return Data

def get_table():
    global Soup
    url = web_url 
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


        table[columns[0].lower().replace(':','').replace(' ','').replace('%20','')] = {column_heads[head[j]]:columns[j] for j in range(len(columns))}
    return table


def get_regions_morocco():
    
    http_client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True



    url = 'http://www.covidmaroc.ma/'
    response = requests.get(url , headers={'X-FRAME-OPTIONS': 'SAMEORIGIN','Connection':'close'})
    response=response.text
    soup = BeautifulSoup(response, "html.parser").select("table")
    Soup = soup[0]
    #scraping the 1st 3 numbers: Cases, deaths and recovered
    head = Soup.select("tr[class='ms-rteTableHeaderRow-6'] th")

    head = [re.sub('[^A-Za-z0-9]+', '', i.text) for i  in head] 

    rows = Soup.select("tr[class='ms-rteTableOddRow-6']") + Soup.select("tr[class='ms-rteTableEvenRow-6']")
    rows = rows[1:]

    table = dict()
    for i in range(len(rows)):
        region_row = rows[i]
        region_name, region_count =  re.sub('[^A-Za-z0-9]+', '',region_row.select("th h2")[0].text) , re.sub('[^A-Za-z0-9]+', '', region_row.select("td h2")[0].text.split('\\')[0])
        
        if region_name!='':
            table[region_name] = region_count
    return table
    