import re
import random
from instagram_api import InstagramApi

from gender_detector import GenderDetector
gender_detector = GenderDetector('us')

INF = 1000000000

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
		del self.depths[user_id]

	def insert(self, users, depth):
		users = [user for user in users if not user.user_id in self.used_bag] # not used
		users = [user for user in users if not user.user_id in self.user_bag] # not already in
		for user in users: self.user_bag[user.user_id] = user
		self.depths[user.user_id] = depth

	def get_depth(self, user_id):
		return self.depths[user_id] 

class InstagramUser:
	def __init__(self, **options):
		self.api = options['api']
		self.user_name = options['user_name']
		self.profile_picture = options['profile_picture']
		self.user_id = options['user_id']
		self.full_name = asciify(options['full_name'])
		self.first_name = self.__get_first_name()
		self.gender = self.__get_gender()
		self._follower_count = None
		self._following_count = None
		self._bio = None 		# lazy init
		self._friends = None 	# lazy init

	def __eq__(self, other):
		return (isinstance(other, self.__class__) and self.user_id == other.user_id)

	def __ne__(self, other):
		return not self.__eq__(other)

	@property
	def follower_count(self):
		if self._follower_count is None:
			user_info = self.api.get_user_info(self.user_id)
			self._follower_count = int(user_info['counts']['followed_by']) if 'counts' in user_info else -1
			self._following_count = int(user_info['counts']['follows']) if 'counts' in user_info else -1
			self._bio = asciify(user_info['bio']) if 'bio' in user_info else ''
		return self._follower_count

	@property
	def following_count(self):
		if self._following_count is None:
			user_info = self.api.get_user_info(self.user_id)
			self._follower_count = int(user_info['counts']['followed_by']) if 'counts' in user_info else -1
			self._following_count = int(user_info['counts']['follows']) if 'counts' in user_info else -1
			self._bio = asciify(user_info['bio']) if 'bio' in user_info else '' 
		return self._following_count

	@property
	def bio(self):
		if self._bio is None: 
			user_info = self.api.get_user_info(self.user_id)
			self._follower_count = int(user_info['counts']['followed_by']) if 'counts' in user_info else -1
			self._following_count = int(user_info['counts']['follows']) if 'counts' in user_info else -1
			self._bio = asciify(user_info['bio']) if 'counts' in user_info else ''
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
	def __init__(self, api, bag, **options):
		self.api = api
		self.bag = bag


	def __get_depth(self, user):
		return self.bag.get_depth(user.user_id)

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
		isFirst = True
		depth = 0
		while True:
			if len(self.bag) > limit: 
				print 'Bag limit reached.'
				exit()
			if len(self.bag) == 0:
				print 'Empty bag.' 
				exit()

			user = self.__get()
			
			depth = self.__get_depth(user)

			if user.gender == 'female':
				if (user.bio.lower().find('kik') != -1 
					or user.bio.lower().find('snap') != -1 
					or user.bio.lower().find('fb') != -1
					or user.bio.lower().find('facebook') != -1):
					print user.user_name, user.bio
			
			# do not go further if the follower count exceeds the following limit
			if (isFirst == False and user.follower_count > follower_limit) or depth + 1 == maxDepth:
				#print 'Follower count exceeded threshold: %s' % user.follower_count
				continue

			isFirst = False
			# fill bag
			self.__insert([friend for friend in user.friends if gender is None or friend.gender == gender], depth + 1) 