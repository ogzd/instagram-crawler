#!/usr/bin/env python

from instagram_api import InstagramApi
from instagram_util import UserIdBag
from gender_detector import GenderDetector

ACCESS_TOKEN = open("access_token.txt").read()
BAG_LIMIT = 1000000

gender_detector = GenderDetector('us')

def search(api, bag):
	while True:
		if len(bag) > BAG_LIMIT: break

		if len(bag) == 0:
			print("Empty bag.")
			exit()

		user_id = bag.pick_random()
		bag.remove(user_id)

		username, fullname, bio = api.get_username_bio(user_id)
		
		# hack on name
		if fullname == None or fullname == '': continue
		if len(fullname.split(' ')) == 1: pass
		if len(fullname.split(' ')) == 2: fullname = fullname.split(' ')[0]
		if len(fullname.split(' ')) == 3: fullname = fullname.split(' ')[0]
		if len(fullname.split(' ')) > 3:  fullname = ''.join(fullname.split(' '))
		if not fullname.isalnum(): continue 

		# detect gender
		gender = gender_detector.guess(fullname)
		print fullname

		if gender == 'female':
			print username, fullname, bio
		
		# fill bag
		user_ids = api.get_accessable_user_ids(user_id)
		bag.insert(user_ids)

def search_by_me():
	api = InstagramApi(ACCESS_TOKEN)
	bag = UserIdBag(api.get_following_ids(api.my_user_id))
	search(api, bag)

def search_by_query(query):
	api = InstagramApi(ACCESS_TOKEN)
	bag = UserIdBag(api.search_users(query))
	search(api, bag)

if __name__ == '__main__':
	search_by_me()

