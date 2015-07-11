import re
import random
import requests
import json
from instagram_api import InstagramApi
from instagram_user import InstagramUser

INF = 1000000000

def get_instagram_user(api, username):
	r = requests.get('http://instagram.com/%s/' % username)
	# parse user block
	index = r.text.find('"user":')
	start = index
	while r.text[index] != '{':
		index += 1
	index += 1
	cnt = 1
	# go until we hit the end of the user block
	while cnt != 0:
		if (r.text[index] == '{'):
			cnt += 1
		elif r.text[index] == '}':
			cnt -= 1
		index += 1

	json_string = "{%s}" % format(r.text[start : index])
	ret = json.loads(json_string)
	return InstagramUser(api = api, 
		user_name = ret['user']['username'],
		profile_picture = ret['user']['profile_pic_url'],
		user_id = ret['user']['id'],
		full_name = ret['user']['full_name'],
		follower_count = ret['user']['followed_by'],
		following_count = ret['user']['follows'],
		biography = ret['user']['biography'])

class InstagramUsers:
	def __init__(self, api, bag, **options):
		self.api = api
		self.bag = bag

	def __get(self):
		user = self.bag.pick('random')
		self.bag.remove(user.user_id)
		return user

	def __insert(self, users, depth):
		self.bag.insert(set(users), depth)

	def search(self, **options):
		limit = options['bag_limit'] if 'limit' in options else 1000000
		gender = options['gender'] if 'gender' in options else None
		maxDepth = options['depth'] if 'depth' in options else INF

		follower_limit = options['follower_limit'] if 'follower_limit' in options else 1000
		depth = 0
		while True:
			if len(self.bag) > limit: 
				print 'Bag limit reached.'
				exit()
			if len(self.bag) == 0:
				print 'Empty bag.' 
				exit()

			user = self.__get()

			depth = self.bag.get_depth(user.user_id)

			if user.gender == 'female':
				if (user.bio.lower().find('kik') != -1 
					or user.bio.lower().find('snap') != -1 
					or user.bio.lower().find('fb') != -1
					or user.bio.lower().find('facebook') != -1):
					print user.user_name, user.bio
			
			# do not go further if the follower count exceeds the following limit
			if (depth != 0 and user.follower_count > follower_limit) or depth + 1 == maxDepth:
				#print 'Follower count exceeded threshold: %s' % user.follower_count
				continue

			# fill bag
			self.__insert([friend for friend in user.friends if gender is None or friend.gender == gender], depth + 1) 