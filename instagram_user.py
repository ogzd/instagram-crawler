from instagram_util import asciify
import re

from gender_detector import GenderDetector
gender_detector = GenderDetector('us')

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

	def __hash__(self):
		return hash(self.user_id);

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