#!/usr/bin/env python
#RMS 2019

import Downloader as DL 
import Selector as PS


def main():

	Poster = DL.PostDownloader()
	Selector = PS.PostSelector()

	posttype = 'news'

	downloaded, story, download_type, pt = Poster.rundownload(posttype=posttype)

	print(downloaded,story,download_type,pt)


##########################
# For debugging

def select():

	Selector = PS.PostSelector()

	selected_post_meta = Selector.select_post(download_type='city')


if __name__ == '__main__':

	#main()
	select()