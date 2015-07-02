#!/usr/bin/env python

from instagram_api import InstagramApi
from instagram_util import UserIdBag
from gender_detector import GenderDetector
import re
import random

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
		first_name = get_first_name(fullname)
		if first_name == None: continue
		
		# detect gender
		gender = gender_detector.guess(first_name)

		if gender == 'female':
			if bio.lower().find("kik") != -1 or bio.lower().find("snap") != -1:
				print username, bio
		
		# fill bag
		add_female_friends(bag, api, user_id)

def add_female_friends(bag, api, user_id):
	bag.insert(get_female_friends(api, user_id))

def get_female_friends(api, user_id):
	# fill bag
	user_ids = api.get_accessable_user_ids(user_id)
	# sample to 100 friends due to request limitations
	user_ids = random.sample(user_ids, min(len(user_ids), 100))
	female_ids = set()
	for user_id in user_ids:
		username, fullname, bio = api.get_username_bio(user_id)
		first_name = get_first_name(fullname)
		if first_name == None: continue
		if gender_detector.guess(first_name) == 'female':
			female_ids.add(user_id)
			if bio.lower().find("kik") != -1 or bio.lower().find("snap") != -1:
				print username, bio
	return female_ids

def get_first_name(fullname):
	# hack on name
	if not fullname or fullname == None: return None
	fullname = fullname.strip()
	if fullname == '': return None
	if len(fullname.split(' ')) == 1: return None
	if len(fullname.split(' ')) == 2: fullname = fullname.split(' ')[0]
	if len(fullname.split(' ')) == 3: fullname = fullname.split(' ')[0]
	if len(fullname.split(' ')) > 3:  fullname = ''.join(fullname.split(' '))
	if not re.match("^[A-Za-z]*$", fullname): return None
	return fullname; 

def search_by_me():
	api = InstagramApi(ACCESS_TOKEN)
	bag = UserIdBag(get_female_friends(api, api.my_user_id))
	search(api, bag)

def search_by_query(query):
	api = InstagramApi(ACCESS_TOKEN)
	bag = UserIdBag(api.search_users(query))
	search(api, bag)

if __name__ == '__main__':
	search_by_me()

