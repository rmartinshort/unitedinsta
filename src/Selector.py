#!/usr/bin/env python
#RMS 2019 

import pandas as pd
import numpy as np
import instaloader
from scrapers import scrape_fleet
from config import config
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import glob
import os
import re 
from datetime import datetime 


class PostSelector():

    def __init__(self,unitedrepo=config.UNITEDREPO,cityrepo=config.CITYREPO) -> None:

        self.unitedrepo = unitedrepo
        self.cityrepo = cityrepo

        self.ACL = instaloader.Instaloader(dirname_pattern=config.UNITEDREPO,download_videos=False,download_video_thumbnails=False)
        self.GL = instaloader.Instaloader(dirname_pattern=config.CITYREPO,download_videos=False,download_video_thumbnails=False)


    def select_post(self,download_type='city',fromid=0):

        '''
        Public

        Select a post to send to instagram. This will return a dataframe of the image we wish to post and its
        associated metadata

        '''

        if download_type in ['city','country']:

            selected_post = self._select_post_generic(self.cityrepo,self.GL)

        elif download_type == 'aircraft':

            aircraft, models = scrape_fleet()

            selected_post = self._select_post_generic(self.unitedrepo,self.ACL,\
                accepted_hashtag_list=models,optional_column_name='aircraft_model',fromid=fromid)

        return selected_post


    def _select_post_generic(self,repo_name,instaloader_instance,
        accepted_hashtag_list=config.CITYHASHTAGS,optional_column_name=None,debug=True,fromid=0):


        posts_info = self._process_posts(fileid=repo_name,L=instaloader_instance)

        posts_info['hashtags'] = posts_info['caption'].apply(self._extract_hashtags)
        posts_info['pcredits'] = posts_info.apply(lambda row: self._extract_pcredits(row),axis=1)
        posts_info['image_size'] = posts_info['Flocation'].apply(self._image_size_check)

        indicator_column = []


        for hashtaglist in posts_info['hashtags']:

            try:
            
                tokens = [str(token).replace('#','') for token in hashtaglist]
                hit = 0
                for token in tokens:
                    if token in accepted_hashtag_list:
                        indicator_column.append(token)
                        hit = 1
                        break

                if hit == 0:
                    indicator_column.append(np.nan)
            
            except:
                
                indicator_column.append(np.nan) 

        if optional_column_name:

            posts_info[optional_column_name] = indicator_column

            try:
                if fromid == 0:
                    chosen_post = posts_info.dropna(subset=['image_size']).sample(1)
                else:
                    chosen_post = posts_info.dropna(subset=[indicator_column,'image_size']).sample(1)
            except:
                print('Fall back to backup post')

                chosen_post = self._get_backup_post()

        else:

            posts_info['indicator'] = indicator_column

            try:
                chosen_post = posts_info.dropna(subset=['indicator','image_size']).sample(1)
            except:
               print('Fall back to backup post')

               chosen_post = self._get_backup_post()

        if debug == True:

            print(chosen_post['caption'].values[0])

            posts_info.dropna(subset=['image_size']).to_csv('Image_size_check.csv')

            image = mpimg.imread(chosen_post['Flocation'].values[0])
            plt.imshow(image)
            plt.axis('off')
            plt.savefig('debug_test.png')

        
        return chosen_post


    def _get_backup_post(self):

        '''
        Generate post from set of backup images
        '''


        repo = np.random.choice([config.BACKUP_IMAGES_AIRCRAFT,config.BACKUP_IMAGES_DESTINATIONS])

        post_meta = {
        'Flocation':[],
        'caption':[],
        'pcredits':[],
        'postdate':[],
        'image_size':[]
        }
            
        chosen_folder = np.random.choice(glob.glob(f'{repo}/*'))

        image_object = chosen_folder.split('/')[-1]
        
        if len(image_object) > 4:
            image_object = ' '.join(re.findall('[A-Z][a-z]*', image_object))
            
        chosen_image = np.random.choice(glob.glob(f'{chosen_folder}/*'))
        
        post_meta['Flocation'].append(chosen_image)
        post_meta['caption'].append(image_object)
        post_meta['pcredits'].append(np.nan)
        post_meta['postdate'].append(np.nan)
        post_meta['image_size'].append(self._image_size_check(chosen_image))
        
        return pd.DataFrame(post_meta)


    def _process_posts(self,fileid,debug=False,L=None) -> pd.DataFrame:
    
        posts_data = glob.glob(f'{fileid}/*.json.xz')
        
        post_metadata = {
            'Flocation':[],
            'caption':[],
            'credits':[],
            'postdate':[],
            'timesincepost':[],
            'nlikes':[],
            'location':[],
            'lon':[],
            'lat':[],
            'ncomments':[],
            'nfollowers':[],
            'nlikes_per_follower':[]
        }
        
        for postmeta in posts_data:
            
            post_name = postmeta.split('.')[0]
            post_image_name = post_name+'.jpg'
            
            if os.path.isfile(post_image_name):

                try:
                
                    print(f'Found post {postmeta}')
                                        
                    metadata = instaloader.load_structure_from_file(context=L.context,\
                        filename=postmeta)
                    
                    #metadata that is useful to us
                    metadata_list = self._get_metadata(metadata)
                    
                    if metadata_list:
                    
                        post_metadata['Flocation'].append(post_image_name)
                        post_metadata['credits'].append(metadata_list[0])
                        post_metadata['caption'].append(metadata_list[1])
                        post_metadata['postdate'].append(metadata_list[3])
                        post_metadata['timesincepost'].append(metadata_list[4])
                        post_metadata['nlikes'].append(metadata_list[5])
                        post_metadata['location'].append(metadata_list[6])
                        post_metadata['lat'].append(metadata_list[7])
                        post_metadata['lon'].append(metadata_list[8])
                        post_metadata['ncomments'].append(metadata_list[9])
                        post_metadata['nfollowers'].append(metadata_list[10])
                        post_metadata['nlikes_per_follower'].append(metadata_list[11])

                except:

                    continue
                    
            
        return pd.DataFrame(post_metadata)

    def _get_metadata(self,metadatafile) -> list:

        username = metadatafile.owner_profile.username
        caption = metadatafile.caption
        caption_hastags = metadatafile.caption_hashtags
        postdate = metadatafile.date
        time_since_postdate = datetime.now() - postdate
        nlikes = metadatafile.likes

        try:
            location_name = metadatafile.location.name
            location_lat = metadatafile.location.lat
            location_lon = metadatafile.location.lng
        except:
            location_name = np.nan
            location_lon = np.nan
            location_lat = np.nan 

        ncomments = metadatafile.comments
        nfollowers = metadatafile.owner_profile.followers
        nlikes_per_follower = nlikes/nfollowers

        return [username,caption,caption_hastags,postdate,time_since_postdate,\
               nlikes,location_name,location_lat,\
               location_lon,ncomments,nfollowers,nlikes_per_follower]

    def _extract_hashtags(self,string) -> list:

        try:
            hashtags = [re.sub(r"(\W+)$", "", j) for j in set([i for i in string.split() if i.startswith("#")])]
        except:
            return np.nan
        if len(hashtags) == 0:
            return np.nan
        else:
            return hashtags

    def _extract_pcredits(self,row) -> list:

        string = row['caption']

        try:
            pcredits = [re.sub(r"(\W+)$", "", j) for j in set([i for i in string.split() if i.startswith("@")])]
            pcredits.append('@'+row['credits'])
        except:
            return np.nan

        return pcredits

    def _image_size_check(self,image_loc) -> tuple:

        image = mpimg.imread(image_loc)

        try:
            (h,w,n) = image.shape
        except:
            return np.nan
        if w < 500:
            return np.nan
        else:
            return (h,w,n)

