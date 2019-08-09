#!/usr/bin/env python
#RMS 2019

import wikipedia as wp
from config import config
from bs4 import BeautifulSoup
import spacy
import requests 
import re
import pandas as pd
from geopy.geocoders import Nominatim
import numpy as np
import os
import datetime


def scrape_fleet(url=config.UNITEDFLEET):

    '''
    Get details of all aircrat operated
    '''


    html = wp.page(url).html().encode("UTF-8")
    aircraft_df = pd.read_html(html)[0]

    aircraft = list(aircraft_df['Aircraft']['Aircraft'])

    aircraft_names = [x.split(' ')[1].split('-')[0] for x in aircraft[:-1]]

    return aircraft,aircraft_names


def scrape_destinations(url=config.UNITEDDESTINATIONS,destfile=config.DESTINATIONS):

    '''
    Get destinations from tthe wiki article, geocode them and return a dataframe
    '''

    if os.path.isfile(destfile):

        destinations_df = pd.read_csv(destfile)

    else:

        html = wp.page("List_of_United_Airlines_destinations").html().encode("UTF-8")
        destinations_df = pd.read_html(html)[0]

        destinations_df['Region'] = destinations_df['Country'].apply(statecol)

        destinations_df['Country'] = destinations_df['Country'].apply(countrycol)

        destinations_df['International'] = destinations_df['Country'].apply(lambda x: 0 if 'United States' in x else 1)

        print('-----------\nGeocoding: This could take a while\n-----------')

        lats,lons = geocodecities(destinations_df['City'])

        destinations_df['LON'] = lons
        destinations_df['LAT'] = lats

        destinations_df[['Country','City','Region','Airport','International','LON','LAT']].to_csv(destfile,index=False)

    return destinations_df




def geocodecities(cities_list):

    '''
    Run geocoding for the cities
    '''

    geolocator = Nominatim(user_agent="rmartinshort")

    destlat = []
    destlon = []

    for city in cities_list:

        if 'Paulo' in city:
            city = "Sao Paulo"
        try:
            location = geolocator.geocode(city)
            destlon.append(location.longitude)
            destlat.append(location.latitude)
        except:
            destlat.append(np.nan)
            destlon.append(np.nan)

    return destlat,destlon


def scrape_news(url=config.UNITEDNEWS,cities_list=[]):

    '''
    Gather recent news articles and return dataframe
    '''

   
    nlp = spacy.load('en_core_web_sm')

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    headlines = soup.find_all('h1',class_='headline')
    dates = soup.find_all('div',class_='article-socialux__meta')

    latest_news = {'Headline':[],'Date':[],'Cities':[]}

    for headline,date in zip(headlines,dates):
        
        headline_text = headline.text
        date = date.text
        
        doc = nlp(headline_text)
        
        #See if any destination cities are mentioned
        #If so, get their names
        
        city_mentions = []
        for token in doc.ents:
            if token.label_ == 'GPE':
                if token.text in cities_list:
                    city_mentions.append(token.text)
        
        latest_news['Headline'].append(headline_text)
        latest_news['Date'].append(date)
        latest_news['Cities'].append(city_mentions)

    news = pd.DataFrame(latest_news)

    now = datetime.datetime.now()
    news['Date'] = pd.to_datetime(news['Date'])
    news['Time_since'] = news['Date'].apply(lambda x: (now - x).days)

    news = news[news['Time_since']<config.NEWSNDAYSMAX]
    news['p'] = news['Time_since'].apply(lambda x: x*(1/news['Time_since'].sum()))

    #probability of choosing that news article
    news['prob'] = list(news['p'].sort_values(ascending=False))

    return news


def statecol(s):
    
    try:
        region_name = re.search(r'\((.*?)\)',s).group(1)
    except:
        region_name = np.nan
    
    return region_name

def countrycol(s):
    
    return re.sub("[\(\[].*?[\)\]]", "", s)


