#!/usr/bin/env python
from instagram_user import InstagramUser
from instagram_user_bag import InstagramUserBag
from instagram_util import InstagramUsers
from instagram_util import get_instagram_user
from instagram_api import InstagramApi
import re

ACCESS_TOKEN = [line.rstrip('\n') for line in open('access_token.txt')][0]
api = InstagramApi(ACCESS_TOKEN)

def search_by_me():	
	bag = InstagramUserBag(InstagramUser(api = api, 
										 user_name = api.data['username'],
										 profile_picture = api.data['profile_picture'],
										 user_id = api.data['id'],
										 full_name = api.data['full_name']))
	users = InstagramUsers(api, bag, access_token = ACCESS_TOKEN)
	users.search(bag_limit = 10000, gender = 'female', depth = 2)

# NOT SUPPORTED ATM
# def search_by_query(query):
# 	users = InstagramUsers(access_token = ACCESS_TOKEN, query = query)
# 	users.search()

if __name__ == '__main__':
	##search_by_me()
	print get_instagram_user(api, "ortschun").user_name


	


