#!/usr/bin/env python
from instagram_user import InstagramUser
from instagram_user_bag import InstagramUserBag
from instagram_users import InstagramUsers
from instagram_api import InstagramApi

import logging
logging.basicConfig()
logger = logging.getLogger('crawler')
logger.setLevel(logging.INFO) # enable debugging

ACCESS_TOKEN = [line.rstrip('\n') for line in open('access_token.txt')][0]
logger.debug('Access token received: %s' % ACCESS_TOKEN)

api = InstagramApi(ACCESS_TOKEN)
logger.debug('Api is initialized for %s' % api.root_user.user_name)

def search_by_me():
	bag = InstagramUserBag(api.root_user)
	logger.debug('User bag is initialized.')
	users = InstagramUsers(api, bag, strategy = 'random')
	logger.debug('Started searching for users..')
	users.search(bag_limit = 10000, gender = 'female', depth = 5)

def search_by_tags(tag):
	tags = api.search_tags(tag)
	tag_name = tags[0]['name'] # tag with most media
	instagram_users = [api.data_to_user(data['user']) for data in api.get_recent_media_by_tag(tag_name)]
	for user_name in set([user.user_name for user in instagram_users]):
		print user_name, api.get_bio_and_follow_info(user_name)
		

# NOT SUPPORTED ATM
# def search_by_query(query):
# 	users = InstagramUsers(access_token = ACCESS_TOKEN, query = query)
# 	users.search()

if __name__ == '__main__':
	search_by_tags('timessquare')
