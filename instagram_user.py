import re
import logging

from threading import Thread
from Queue import Queue
from gender_detector import GenderDetector

gender_detector = GenderDetector('us')

logger = logging.getLogger('crawler.instagram_user')

THREAD_COUNT = 5
q = Queue(THREAD_COUNT * 2)

class InstagramUser:
	def __init__(self, **options):
		self.api = options['api']
		self.user_name = options['user_name']
		self.profile_picture = options['profile_picture']
		self.user_id = options['user_id']
		self.full_name = self.__asciify(options['full_name']) if options['full_name'] else None
		self.first_name = self.__get_first_name()
		self.gender = self.__get_gender()
		self.follower_count = options['follower_count']
		self.following_count = options['following_count']
		self.bio = '' if options['biography'] is None else options['biography']
		self._friends = None 	# lazy init

	def __eq__(self, other):
		return (isinstance(other, self.__class__) and self.user_id == other.user_id)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(self.user_id);


	def __asciify(self, txt):
		return re.sub(r'[^\x00-\x7F]+','', self.__utf8(txt))

	def __utf8(self, txt):
		return txt.encode('utf-8').strip().lower()

	@property
	def friends(self):
		if self._friends is None: 
			logger.debug('Requesting friends info for user: %s' % self.user_name) 
			for i in range(THREAD_COUNT):
			    t = Thread(target=self.addFriends)
			    t.daemon = True
			    t.start()
			self._friends = set()
			usernames = [data['username'] for data in self.api.get_friends_infos(self.user_id)]
			for username in usernames:
				q.put(username)
			q.join()
		return self._friends

	def addFriends(self):
		while True:
			username = q.get()
			user = self.api.get_instagram_user(username)
			self._friends.add(user)
			q.task_done()

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