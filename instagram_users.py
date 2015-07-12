import re
import random
import requests
from instagram_api import InstagramApi
from instagram_user import InstagramUser

import logging
logger = logging.getLogger('crawler.instagram_users')

INF = 1000000000

class InstagramUsers:
	def __init__(self, api, bag, **options):
		self.api = api
		self.bag = bag
		self.strategy = options['strategy'] if 'strategy' in options else 'random'

	def __get(self):
		user = self.bag.pick(self.strategy)
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
				logger.error('Bag limit reached.')
				exit()
			if len(self.bag) == 0:
				logger.error('Empty bag.') 
				exit()

			user = self.__get()
			logger.debug('Searching for %s' % user.user_name)

			depth = self.bag.get_depth(user.user_id)
			logger.debug('Depth of %s: %s' % (user.user_name, depth))

			if user.gender == 'female':
				if (user.bio.lower().find('kik') != -1 
					or user.bio.lower().find('snap') != -1 
					or user.bio.lower().find('fb') != -1
					or user.bio.lower().find('facebook') != -1):
					print user.user_name, user.bio

			# do not go further if the follower count exceeds the following limit
			if (depth != 0 and user.follower_count > follower_limit) or depth + 1 == maxDepth:
				logger.debug('Follower count exceeded threshold: %s' % user.follower_count)
				continue

			# fill bag
			logger.debug('Inflating the bag with friends info')
			self.__insert([friend for friend in user.friends if gender is None or friend.gender == gender], depth + 1) 