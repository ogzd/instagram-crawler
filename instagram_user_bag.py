import random

import logging
logger = logging.getLogger('crawler.instagram_user_bag')

class InstagramUserBag:

	def __init__(self, init_user):
		# store Instagram User's data
		self.user_bag = { init_user.user_id: init_user }  
		# store used user ids
		self.used_bag = set()
		self.depths = dict()
		self.depths[init_user.user_id] = 0
		self.pick_strategy = { 'random': self.__pick_random, 'fifo': self.__pick_fifo }

	def __len__(self):
		return len(self.user_bag)

	def pick(self, strategy):
		return self.pick_strategy[strategy]()  

	def __pick_random(self):
		return random.sample(self.user_bag.values(), 1)[0]

	def __pick_fifo(self):
		return self.user_bag.values()[0]

	def remove(self, user_id):
		self.user_bag.pop(user_id, None)
		self.used_bag.add(user_id)

	def insert(self, users, depth):
		users = [user for user in users if not user.user_id in self.used_bag] # not used
		users = [user for user in users if not user.user_id in self.user_bag] # not already in
		for user in users:
			self.user_bag[user.user_id] = user
			self.depths[user.user_id] = depth


	def get_depth(self, user_id):
		return self.depths[user_id] 