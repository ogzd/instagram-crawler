import requests, re, json, logging
from instagram_user import InstagramUser

import logging
logger = logging.getLogger('crawler.instagram_api')

INSTAGRAM_USER_SEARCH = 'https://api.instagram.com/v1/users/search?q=%s&access_token=%s'
INSTAGRAM_USER_BASIC = 'https://api.instagram.com/v1/users/%s/?access_token=%s'
INSTAGRAM_SELF_URL = 'https://api.instagram.com/v1/users/self?access_token=%s'
INSTAGRAM_FOLLOWEDBY_URL = 'https://api.instagram.com/v1/users/%s/followed-by?access_token=%s'
INSTRAGRAM_FOLLOWS_URL = 'https://api.instagram.com/v1/users/%s/follows?access_token=%s'

MAX_PAGINATION_LIMIT = 2

class InstagramApi:

	def __init__(self, access_token):
		requests.packages.urllib3.disable_warnings()
		r = requests.get(INSTAGRAM_SELF_URL % access_token).json()
		self.root_user = self.data_to_user(r['data'])
		self.access_token = access_token

	def get_followedby_infos(self, user_id):
		logger.debug('Getting followedby infos for user: %s' % user_id)
		return self.__get_infos(user_id, INSTAGRAM_FOLLOWEDBY_URL % (user_id, self.access_token))

	def get_following_infos(self, user_id):
		logger.debug('Getting following infos for user: %s' % user_id)
		return self.__get_infos(user_id, INSTRAGRAM_FOLLOWS_URL % (user_id, self.access_token))

	# TODO: refactor this code.
	def __get_infos(self, user_id, url):
		infos = []
		call_count = 0
		while url:
			r = requests.get(url).json()
			call_count = call_count + 1
			if not 'meta' in r or r['meta']['code'] != 200: return infos
			infos += r['data']
			if 'next_url' not in r['pagination']: 
				break
			if call_count == MAX_PAGINATION_LIMIT:
				break
			url = r['pagination']['next_url']
		return infos

	# HTML scrapping code for retrieving bio and follower info
	def get_bio_and_follow_info(self, username):
		logger.debug('Getting instagram user by html request for user: %s' % username)
		r = requests.get('http://instagram.com/%s/' % username)
		# parse user block
		index = r.text.find('"user":')
		start = index
		while r.text[index] != '{':
			index += 1
		index += 1
		cnt = 1
		ignore = False
		# go until we hit the end of the user block
		while cnt != 0:
			if r.text[index] == '"' and r.text[index - 1] != '\\': # string start / end position
				ignore = not ignore
			if not ignore and r.text[index] == '{':
				cnt += 1
			elif not ignore and r.text[index] == '}':
				cnt -= 1
			index += 1

		json_string = '{%s}' % r.text[start : index]
		logger.debug('JSON data for user:\n%s' % json_string)
		ret = json.loads(json_string)

		return ('' if ret['user']['biography'] is None else self.__asciify(ret['user']['biography']), 
				0 if ret['user']['followed_by']['count'] is None else ret['user']['followed_by']['count'], 
				0 if ret['user']['follows']['count'] is None else ret['user']['follows']['count'])

	def search_users(self, query):
		logger.debug('Searching instagram users by query: %s' % query)
		r = requests.get(INSTAGRAM_USER_SEARCH % (query, self.access_token)).json()
		return set([data['id'] for data in r['data']]) if 'meta' in r and r['meta']['code'] == 200 else set()

	# return only following data
	def get_friends_infos(self, user_id):
		logger.debug('Getting friends infos for user: %s' % user_id)
		return self.get_following_infos(user_id)

	def __asciify(self, txt):
		return re.sub(r'[^\x00-\x7F]+','', self.__utf8(txt))

	def __utf8(self, txt):
		return txt.encode('utf-8').strip().lower()

	def data_to_user(self, data):
		user_id = data['id'] if 'id' in data else None
		user_name = data['username'] if 'username' in data else None
		profile_picture = data['profile_picture'] if 'profile_picture' in data else None
		full_name = self.__asciify(data['full_name']) if 'full_name' in data else None
		return InstagramUser(api = self, 
							user_id = user_id,
							user_name = user_name,
							profile_picture = profile_picture,
							full_name = full_name) 