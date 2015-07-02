#!/usr/bin/env python

from instagram_util import InstagramUsers

ACCESS_TOKEN = open("access_token.txt").read()

# def add_female_friends(bag, api, user_id):
# 	bag.insert(get_female_friends(api, user_id))

# def get_female_friends(api, user_id):
# 	# fill bag
# 	user_ids = api.get_accessable_user_ids(user_id)
# 	# sample to 100 friends due to request limitations
# 	user_ids = random.sample(user_ids, min(len(user_ids), 100))
# 	female_ids = set()
# 	for user_id in user_ids:
# 		username, fullname, bio = api.get_username_bio(user_id)
# 		first_name = get_first_name(fullname)
# 		if first_name == None: continue
# 		if gender_detector.guess(first_name) == 'female':
# 			female_ids.add(user_id)
# 			if bio.lower().find("kik") != -1 or bio.lower().find("snap") != -1:
# 				print username, bio
# 	return female_ids

def search_by_me():
	users = InstagramUsers(access_token = ACCESS_TOKEN)
	users.search(bag_limit = 10000, gender = 'female')

# NOT SUPPORTED ATM
# def search_by_query(query):
# 	users = InstagramUsers(access_token = ACCESS_TOKEN, query = query)
# 	users.search()

if __name__ == '__main__':
	search_by_me()

