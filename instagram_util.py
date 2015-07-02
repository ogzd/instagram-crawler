import re
import random
from instagram_api import InstagramApi

def utf8(txt):
	return txt.encode('utf-8').strip().lower()

def asciify(txt):
	return re.sub(r'[^\x00-\x7F]+',' ', utf8(txt))

class UserIdBag:
	def __init__(self, init_bag):
		self.user_id_bag = init_bag
		self.used_bag = set()

	def __len__(self):
		return len(self.user_id_bag)

	def pick_random(self):
		return random.sample(self.user_id_bag, 1)[0]

	def remove(self, user_id):
		self.user_id_bag -= set([user_id])
		self.used_bag |= set([user_id])

	def insert(self, user_ids):
		user_ids = user_ids - self.used_bag
		self.user_id_bag = self.user_id_bag | user_ids

class InstagramUser:
	def __init__(self, options):
		self.api = options['api']
		self.user_id = options['user_id']
		self.full_name, self.bio = self.get_details()

	def get_details(self):
		return self.api.get_username_bio(self.user_id)

class InstagramUsers:
	def __init__(self, **options):
		self.access_token = options['access_token']
		self.api = InstagramApi(self.access_token)
		if 'init_bag' in options: self.bag = UserIdBag(options['init_bag'])
		elif 'query' in options: self.bag = UserIdBag(api.search_users(options['query']))
		else self.bag = UserIdBag(set([api.my_user_id]))

	def get(self):
		user_id = self.bag.pick_random()
		self.bag.remove(user_id)
		

	def insert(self, user_ids):
		self.bag.insert(user_ids)

