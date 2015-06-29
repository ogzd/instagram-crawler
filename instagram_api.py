import requests
from instagram_util import asciify

CLIENT_ID 		= 'd6244e297ac24ceeb7e40bd2a8115e6a'
CLIENT_SECRET 	= '000ccb0537314540b4a60904072b4242'
REDIRECT_URI	= 'http://ogzd.me'

INSTAGRAM_USER_SEARCH = 'https://api.instagram.com/v1/users/search?q=%s&access_token=%s'
INSTAGRAM_USER_BASIC = 'https://api.instagram.com/v1/users/%s/?access_token=%s'
INSTAGRAM_SELF_URL = 'https://api.instagram.com/v1/users/self?access_token=%s'
INSTAGRAM_FOLLOWEDBY_URL = 'https://api.instagram.com/v1/users/%s/followed-by?access_token=%s'
INSTRAGRAM_FOLLOWS_URL = 'https://api.instagram.com/v1/users/%s/follows?access_token=%s'

class InstagramApi:

	def __init__(self, access_token):
		r = requests.get(INSTAGRAM_SELF_URL % access_token).json()
		self.my_user_id = r['data']['id']
		self.access_token = access_token

	def get_followedby_ids(self, user_id):
		r = requests.get(INSTAGRAM_FOLLOWEDBY_URL % (user_id, self.access_token)).json()
		return set([data['id'] for data in r['data']]) if r['meta']['code'] == 200 else set()

	def get_following_ids(self, user_id):
		r = requests.get(INSTRAGRAM_FOLLOWS_URL % (user_id, self.access_token)).json()
		return set([data['id'] for data in r['data']]) if r['meta']['code'] == 200 else set() 

	def get_username_bio(self, user_id):
		r = requests.get(INSTAGRAM_USER_BASIC % (user_id, self.access_token)).json()
		return (r['data']['username'], asciify(r['data']['full_name']), asciify(r['data']['bio'])) if r['meta']['code'] == 200 else (user_id, None, 'Not Allowed')

	def search_users(self, query):
		r = requests.get(INSTAGRAM_USER_SEARCH % (query, self.access_token)).json()
		return set([data['id'] for data in r['data']]) if r['meta']['code'] == 200 else set()

	def get_accessable_user_ids(self, user_id):
		return self.get_following_ids(user_id) | self.get_followedby_ids(user_id)