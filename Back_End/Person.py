class Person:
	def __init__(self, uid=None, name=None, postcode=None):
		self._id = uid
		self._name = name
		self._postcode = postcode
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
	def address(self):
		return self._address

	@address.setter
	def address(self, address):
		self._address = address

	@property
	def orders(self):
		return self._orders

	def new_order(self, order):
		if self._orders:
			n_key = max(self._orders.keys()) + 1
			self._orders[n_key] = order
		else:
			self._orders[1] = order
	
	@property
	def postcode(self):
		return self._postcode
