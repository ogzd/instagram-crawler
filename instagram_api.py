import requests, re, random

INSTAGRAM_USER_SEARCH = 'https://api.instagram.com/v1/users/search?q=%s&access_token=%s'
INSTAGRAM_USER_BASIC = 'https://api.instagram.com/v1/users/%s/?access_token=%s'
INSTAGRAM_SELF_URL = 'https://api.instagram.com/v1/users/self?access_token=%s'
INSTAGRAM_FOLLOWEDBY_URL = 'https://api.instagram.com/v1/users/%s/followed-by?access_token=%s'
INSTRAGRAM_FOLLOWS_URL = 'https://api.instagram.com/v1/users/%s/follows?access_token=%s'

MAX_PAGINATION_LIMIT = 2

class InstagramApi:

	def __init__(self, access_token):
		r = requests.get(INSTAGRAM_SELF_URL % access_token).json()
		self.data = r['data']
		self.access_token = access_token

	def get_followedby_infos(self, user_id):
		return self.__get_infos(user_id, INSTAGRAM_FOLLOWEDBY_URL % (user_id, self.access_token))

	def get_following_infos(self, user_id):
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

	def get_user_info(self, user_id):
		r = requests.get(INSTAGRAM_USER_BASIC % (user_id, self.access_token)).json()
		return r['data'] if 'meta' in r and r['meta']['code'] == 200 else {}

	def get_bio(self, user_id):
		user_info = self.get_user_info(user_id)
		return user_info['bio'] if 'bio' in user_info else ''

	def search_users(self, query):
		r = requests.get(INSTAGRAM_USER_SEARCH % (query, self.access_token)).json()
		return set([data['id'] for data in r['data']]) if 'meta' in r and r['meta']['code'] == 200 else set()

	def get_friends_infos(self, user_id):
		print 'Getting friend of %s' % user_id
		d = {}
		for data in self.get_followedby_infos(user_id): d[data['id']] = data
		for data in self.get_following_infos(user_id): d[data['id']] = data
		return d.values()