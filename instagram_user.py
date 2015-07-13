import re

from gender_detector import GenderDetector
gender_detector = GenderDetector('us')

import logging
logger = logging.getLogger('crawler.instagram_user')

class InstagramUser:
	def __init__(self, **options):
		self.api = options['api']
		self.user_name = options['user_name']
		self.profile_picture = options['profile_picture']
		self.user_id = options['user_id']
		self.full_name = options['full_name']
		self.first_name = self.__get_first_name()
		self.gender = self.__get_gender()
		# lazy init (these data are initialized all together when a query for any of them is made.)
		self._follower_count = None
		self._following_count = None
		self._bio = ''
		self._friends = None

	def __eq__(self, other):
		return (isinstance(other, self.__class__) and self.user_id == other.user_id)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(self.user_id);

	@property
	def friends(self):
		if self._friends is None:
			logger.debug('Requesting friends info for user: %s' % self.user_name) 
			self._friends = [self.api.data_to_user(data) for data in self.api.get_friends_infos(self.user_id)]
		return self._friends

	@property
	def bio(self):
		if self._bio is '':
			logger.debug('Initializing lazy info for user: %s' % self.user_name)
			self._bio, self._follower_count, self._following_count = self.api.get_bio_and_follow_info(self.user_name)
		return self._bio

	@property
	def follower_count(self):
		if self._follower_count is None:
			logger.debug('Initializing lazy info for user: %s' % self.user_name)
			self._bio, self._follower_count, self._following_count = self.api.get_bio_and_follow_info(self.user_name)
		return self._follower_count

	@property
	def following_count(self):
		if self._following_count is None:
			logger.debug('Initializing lazy info for user: %s' % self.user_name)
			self._bio, self._follower_count, self._following_count = self.api.get_bio_and_follow_info(self.user_name)
		return self._following_count

	def __get_gender(self):
		logger.debug('Guessing gender for user: %s' % self.user_name)
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
		if not re.match('^[A-Za-z]*$', fullname): return None
		return fullname; 