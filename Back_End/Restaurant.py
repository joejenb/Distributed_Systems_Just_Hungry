class Restaurant:
	def __init__(self, uid=None, name=None, cuisine=None, dishes=None):
		self._id = uid
		self._name = name
		self._cuisine = cuisine
		self._dishes = dishes
		self._orders = {}

	@property
	def id(self):
		return self._id

	@id.setter
	def id(self, uid):
		self._id = uid

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, name):
		self._name = name

	@property
	def orders(self):
		return self._orders

	@property
	def dishes(self):
		return self._dishes

	def new_order(self, dish):
		if dish in self._dishes:
			n_key = max(self._orders.keys()) + 1 if self._orders else 1
			self._orders[n_key] = dish
			return {"Order-Number": n_key, "Success": True}
		return {"Success": False}

	def deliver(self, ord_num):
		order = self._orders[ord_num]
		if order:
			return {"Success": True, "Order": order}
		return {"Success": False}
