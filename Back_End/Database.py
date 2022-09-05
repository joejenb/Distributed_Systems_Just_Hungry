import Pyro4

class Database:
	def __init__(self, restaurants):
		self.restaurants = restaurants
		self.users = {}
		self.orders = {}
		self.requests = {}

	def add_request(self, request_id, response):
		self.requests[request_id] = response	

	def get_key(self, key_type):
		if key_type == "users" and self.users:
			n_key = max(self.users.keys()) + 1
		elif key_type == "orders" and self.orders:
			n_key = max(self.orders.keys()) + 1
		else:
			n_key = 1
		return n_key

