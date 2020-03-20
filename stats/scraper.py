import requests
import urllib.request
from bs4 import BeautifulSoup
import time

Soup = ''

attributes = [
    {'top' : 'Currently Infected Patients',
    'left': 'in Mild Condition',
    'right': 'Serious or Critical'},

    {'top' : 'Cases which had an outcome',
    'left': 'Recovered / Discharged',
    'right': 'Deaths'},

]

countries = {
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
    global Soup, Last_Time

    url = web_url + "country/" + countries[country_id]
    response = requests.get(url).text
    Last_Time = time.time()
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

    Data['country'] = countries[country_id]
    return Data

def get_table():
    global Soup, Last_Time

    url = web_url 
    response = requests.get(url).text
    soup = BeautifulSoup(response, "html.parser")
    Soup = soup.select("table[id='main_table_countries_today']")[0]

    #scraping the 1st 3 numbers: Cases, deaths and recovered
    head = Soup.select("th")
    head = {j : i.text.replace(',', ' ') for j,i  in enumerate(head)}

    rows = Soup.select("tbody tr")

    table = dict()
    for i in range(len(rows)):
        country_row = rows[i]
        columns = [i.text.strip() for i in country_row.select('td')]

        table[columns[0].lower().replace(':','')] = {head[j]:columns[j] for j in range(len(columns))}
    return table