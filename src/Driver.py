#!/usr/bin/env python
#RMS 2019

import Downloader as DL 
import Selector as PS
import os
import numpy as np
import time 

def main():

    Poster = DL.PostDownloader()
    Selector = PS.PostSelector()

    posttype = 'general'

    print('Running download')

    downloaded, story, download_type, pt, fromid = Poster.rundownload(posttype=posttype)

    print(download_type)

    print('Selecting post meta')

    selected_post_meta = Selector.select_post(download_type=download_type,fromid=fromid)

    print(downloaded,story,download_type,pt,selected_post_meta)
    print(selected_post_meta.columns)

    #Caption can be designed with input from post_meta and story.

    print ('Designing caption...')


def post_experiment():

    '''Experiment where we try generating a series of posts'''

    Poster = DL.PostDownloader()
    Selector = PS.PostSelector()

    if not os.path.exists('experiment_posts'):
        os.mkdir('experiment_posts')

    for postnumber in range(100):

        try:

            posttype = np.random.choice(['news','general'],p=[0.2,0.8])

            print('Running download')

            downloaded, story, download_type, pt = Poster.rundownload(posttype=posttype)

            print('Selecting post meta')

            selected_post_meta = Selector.select_post(download_type=download_type)

            print(downloaded,story,download_type,pt,selected_post_meta)
            post_image = 'post_%03d.jpg' %postnumber
            os.system('mv debug_test.png experiment_posts/%s' %post_image)
            print('Done post number %i' %postnumber)
            print('----------------------------------------------------------------')

        except:

            print('Wait 10 seconds, try again')
            time.sleep(10)



##########################
# For debugging

def select():

    Selector = PS.PostSelector()

    selected_post_meta = Selector.select_post(download_type='city')


if __name__ == '__main__':

    main()
    #post_experiment()
    #main()