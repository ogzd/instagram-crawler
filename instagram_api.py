import requests, re, json
from instagram_user import InstagramUser

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

	def get_instagram_user(self, username):
		r = requests.get('http://instagram.com/%s/' % username)
		# parse user block
		index = r.text.find('"user":')
		start = index
		while r.text[index] != '{':
			index += 1
		index += 1
		cnt = 1
		# go until we hit the end of the user block
		while cnt != 0:
			if (r.text[index] == '{'):
				cnt += 1
			elif r.text[index] == '}':
				cnt -= 1
			index += 1

		json_string = "{%s}" % format(r.text[start : index])
		ret = json.loads(json_string)
		return InstagramUser(api = self, 
			user_name = ret['user']['username'],
			profile_picture = ret['user']['profile_pic_url'],
			user_id = ret['user']['id'],
			full_name = ret['user']['full_name'],
			follower_count = ret['user']['followed_by'],
			following_count = ret['user']['follows'],
			biography = ret['user']['biography'])

	def search_users(self, query):
		r = requests.get(INSTAGRAM_USER_SEARCH % (query, self.access_token)).json()
		return set([data['id'] for data in r['data']]) if 'meta' in r and r['meta']['code'] == 200 else set()

	def get_friends_infos(self, user_id):
		d = {}
		for data in self.get_following_infos(user_id): d[data['id']] = data
		return d.values()