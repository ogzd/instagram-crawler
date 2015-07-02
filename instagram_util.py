import re
import random

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
	def __init__(self, **userInfo):
		self.user_id = userInfo['user_id']
		self.full_name = userInfo['full_name']
		self.bio = userInfo['bio']