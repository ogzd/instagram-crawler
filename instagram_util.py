import re
import random
from instagram_api import InstagramApi

INF = 1000000000

def utf8(txt):
	return txt.encode('utf-8').strip().lower()

def asciify(txt):
	return re.sub(r'[^\x00-\x7F]+','', utf8(txt))

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