#!/usr/bin/env/python 

import os

#Will not work when a crontab is used!
current_dir = os.getcwd()
PACKAGE_ROOT = '/'.join(current_dir.split('/')[:-1])
DATASETS = PACKAGE_ROOT+'/data'
MODELS = PACKAGE_ROOT+'/classifiers'
POSTS = PACKAGE_ROOT+'/post_database'

UNITEDREPO = PACKAGE_ROOT+'/unitedrepo'
CITYREPO = PACKAGE_ROOT+'/cityrepo'

if not os.path.exists(DATASETS):

	os.system('mkdir %s' %DATASETS)

if not os.path.exists(UNITEDREPO):

	os.system('mkdir %s' %UNITEDREPO)

if not os.path.exists(CITYREPO):

	os.system('mkdir %s' %CITYREPO)

POST_TYPES = ['City','CityInternational','Airplane','News']

UNITEDFLEET = "United_Airlines_fleet"
UNITEDDESTINATIONS = "List_of_United_Airlines_destinations"

UNITEDNEWS = "https://hub.united.com/newsroom-routes/"

DESTINATIONS = DATASETS+'/Destinations.csv'

#number of hours between posts
POST_FREQ = 6
#numer of posts between attempt to gather latest news
POST_NEWS_GATHER = 10

NEWSNDAYSMAX = 50

#number of posts to download during every attempt
POSTLIMIT = 10

#Hashtag for aircraft images
UNITEDHASHTAG = 'UnitedAirlines'

#Hashtags needed to accept a city image
CITYHASHTAGS = ["cityscape","skyline","cityscapes","architecture"]




