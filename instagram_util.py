import re
import random
from instagram_api import InstagramApi

from gender_detector import GenderDetector
gender_detector = GenderDetector('us')

def utf8(txt):
	return txt.encode('utf-8').strip().lower()

def asciify(txt):
	return re.sub(r'[^\x00-\x7F]+','', utf8(txt))

class InstagramUserBag:
	def __init__(self, init_user):
		# store Instagram User's data
		self.user_bag = { init_user.user_id: init_user }  
		# store used user ids
		self.used_bag = set()

	def __len__(self):
		return len(self.user_bag)

	def pick_random(self):
		return random.sample(self.user_bag.values(), 1)[0]

	def remove(self, user_id):
		self.user_bag.pop(user_id, None)
		self.used_bag.add(user_id)

	def insert(self, users):
		users = [user for user in users if not user.user_id in self.used_bag] # not used
		users = [user for user in users if not user.user_id in self.user_bag] # not already in
		for user in users: self.user_bag[user.user_id] = user

class InstagramUser:
	def __init__(self, **options):
		self.api = options['api']
		self.user_name = options['user_name']
		self.profile_picture = options['profile_picture']
		self.user_id = options['user_id']
		self.full_name = asciify(options['full_name'])
		self.first_name = self.__get_first_name()
		self.gender = self.__get_gender()
		self._bio = None 		# lazy init
		self._friends = None 	# lazy init

	@property
	def bio(self):
		if self._bio is None: 
			self._bio = asciify(self.api.get_bio(self.user_id))
		return self._bio

	@property
	def friends(self):
		if self._friends is None: 
			self._friends = [InstagramUser(api = self.api, 
										user_name = data['username'],
										profile_picture = data['profile_picture'],
										user_id = data['id'],
										full_name = data['full_name']) for data in self.api.get_friends_infos(self.user_id)]
		return self._friends

	def __get_gender(self):
		return gender_detector.guess(self.first_name) if self.first_name != None else 'unknown' 

	def __get_first_name(self):
		fullname = self.full_name
		if not fullname or fullname == None: return None
		fullname = fullname.strip()
		if fullname == '': return None
		if len(fullname.split(' ')) == 1: return None
		if len(fullname.split(' ')) == 2: fullname = fullname.split(' ')[0]
		if len(fullname.split(' ')) == 3: fullname = fullname.split(' ')[0]
		if len(fullname.split(' ')) > 3:  fullname = ''.join(fullname.split(' '))
		if not re.match("^[A-Za-z]*$", fullname): return None
		return fullname; 

class InstagramUsers:
	def __init__(self, **options):
		self.access_token = options['access_token']
		self.api = InstagramApi(self.access_token)
		self.bag = InstagramUserBag(InstagramUser(api = self.api, 
												user_name = self.api.data['username'],
												profile_picture = self.api.data['profile_picture'],
												user_id = self.api.data['id'],
												full_name = self.api.data['full_name']))

	def __get(self):
		user = self.bag.pick_random()
		self.bag.remove(user.user_id)
		return user

	def __insert(self, users):
		self.bag.insert(set(users))

	def search(self, **options):
		limit = options['limit'] if 'limit' in options else 1000000
		gender = options['gender'] if 'gender' in options else None

		while True:
			if len(self.bag) > limit: 
				print 'Bag limit reached.'
				exit()
			if len(self.bag) == 0:
				print 'Empty bag.' 
				exit()

			user = self.__get()
			print user.user_id, user.full_name, user.gender 

			if user.gender == 'female':
				if user.bio.lower().find('kik') != -1 or user.bio.lower().find('snap') != -1:
					print user.user_name, user.bio
			
			# fill bag
			self.__insert([friend for friend in user.friends if gender is None or friend.gender == gender]) 