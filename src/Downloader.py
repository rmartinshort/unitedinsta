#!/usr/bin/env python
#RMS 2019 

import numpy as np
import pandas as pd 
import instaloader
import re
import os
from datetime import datetime
from config import config
import scrapers as webscrape

class PostDownloader():

    def __init__(self,posttypes=config.POST_TYPES) -> None:

        self.post_types = posttypes

        self.ACL = instaloader.Instaloader(dirname_pattern=config.UNITEDREPO,download_videos=False,download_video_thumbnails=False)
        self.GL = instaloader.Instaloader(dirname_pattern=config.CITYREPO,download_videos=False,download_video_thumbnails=False)


    def rundownload(self,posttype='general'):

        '''
        Download wrapper
        '''

        self._delete_repos()

        ## OPTION 1: posting cities or aircraft

        if posttype == 'general':

            pt = self._decidetype()

            print(f'Download type is {pt}')

            if 'City' in pt:

                downloaded, destination, download_type = self._downloadcityposts(pt)

            else:

                downloaded, destination, download_type = self._downloadaircraftposts(pt)


            return downloaded, destination, download_type, pt


        ## OPTION 2: posting news

        else:
            pt = "News"

            downloaded, selected_story, download_type = self._selectnews()

            return downloaded, selected_story, download_type, pt 



    def _decidetype(self) -> str:

        '''Choose the type of post'''

        index = np.random.randint(low=0,high=3)
        post_type = self.post_types[index]

        return post_type


    def _selectnews(self,posttype='News'):

        '''
        Get posts associated with a news story
        '''


        destinations = self._getdestinations()

        if posttype == 'News':

            cities_list = list(destinations['City'])

            news_stories = self._get_news(cities=cities_list)

            print(news_stories)

            news_index = np.random.choice(np.arange(len(news_stories)),p=news_stories['prob'].values)

            selected_story = news_stories.iloc[news_index]

            if len(selected_story['Cities']) > 0:

                city = np.random.choice(selected_story['Cities'])

                hashtag = ''.join(city.split())+'cityscape'

                downloaded = self._download_posts(downloader=self.GL,hashtag=hashtag)
                download_type = 'city'

                if downloaded == False:

                    downloaded = self._downloadaircraftposts()
                    download_type = 'aircraft'

        return downloaded, selected_story, download_type



    def _downloadcityposts(self,posttype='City'):

        '''
        Get posts associated with a city
        '''

        aircraft = self._getfleet()

        destinations = self._getdestinations()

        if posttype == 'City':

            destinations = destinations[destinations['International']==0]

        elif posttype == 'CityInternational':

            destinations = destinations[destinations['International']==1]

        destination_index = np.random.randint(low=0,high=len(destinations)-1)
        
        destination = destinations.iloc[destination_index]
        
        city = destination['City']
        country = destination['Country']
        region = destination['Region']
        airport = destination['Airport']
        
        print(city,country,region,airport)
        
        #Attempt 1: cityscape
        
        downloaded = False
        
        hashtag = ''.join(city.split())+'cityscape'
        
        print(f'Attempting download for {hashtag}')
        
        downloaded = self._download_posts(downloader=self.GL,hashtag=hashtag)
        download_type = 'city'

        # Attempt 2: city general
        if downloaded == False:
            
            hashtag = ''.join(city.split()).lower()
            print(f'Attempting download for {hashtag}')
            downloaded = self._download_posts(downloader=self.GL,hashtag=hashtag)
            download_type = 'city'
        
        # Attempt 3: country
        if downloaded == False:
            
            hashtag = ''.join(country.split()).lower()
            print(f'Attempting download for {hashtag}')
            downloaded = self._download_posts(downloader=self.GL,hashtag=hashtag)
            download_type = 'country'
        
        
        return downloaded, destination, download_type

    def _downloadaircraftposts(self,hashtag=config.UNITEDHASHTAG) -> bool:

        '''
        Get posts associated with aircraft
        '''

        downloaded = self._download_posts(downloader=self.ACL,hashtag=hashtag)
        download_type = 'aircraft'

        return downloaded, None, download_type


    def _getfleet(self) -> tuple:

        '''
        Return airfract names and models
        '''

        aircraft,models = webscrape.scrape_fleet()

        return (aircraft,models)

    def _getdestinations(self) -> pd.DataFrame:

        '''
        Return destinations dataframe
        '''

        destinations = webscrape.scrape_destinations()

        return destinations

    def _get_news(self,cities) -> pd.DataFrame:

        '''
        Return news dataframe
        '''

        news = webscrape.scrape_news(cities_list=cities)

        return news

    def _download_posts(self,downloader,limit=config.POSTLIMIT,hashtag='city') -> bool:

        '''
        Use instaloader to download post images and metadata
        '''
    
        try:
            i = 0
            for post in downloader.get_hashtag_posts(hashtag):
                downloader.download_post(post, target='#'+hashtag)
                if i >= limit:
                    break
                i += 1
            return True
        except:
            return False

    def _delete_repos(self) -> None:

        '''
        Remove repos from previous download attempt
        '''

        os.system('rm -rf %s' %config.UNITEDREPO)
        os.system('rm -rf %s' %config.CITYREPO)







