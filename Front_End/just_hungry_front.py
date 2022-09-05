import Pyro4

class Just_Hungry:
	def __init__(self, primary_server):
		self.primary_server = primary_server 
		self._view = []

	@Pyro4.expose
	def order(self, user_id, res_id, item_id):
		while self.primary_server:
			try:
				order_id, self._view, err = self.primary_server.new_order(user_id, res_id, item_id)
				return order_id, err
			except Exception:
				self.primary_server = self.find_primary()
		return False, True 

	@Pyro4.expose
	def get_orders(self, order_id):
		while self.primary_server:
			try:
				order_stat, self._view, err = self.primary_server.get_orders(order_id)
				return order_stat, err
			except Exception:
				self.primary_server = self.find_primary()
		return False, True
	
	@Pyro4.expose
	def get_restaurants(self):
		'''Front end is successfully connecting to primary server, it is then sending get_restaurants requests which are recieved, return 
		of backend is causing an error when being assigned to variables on front end'''
		while self.primary_server:
			try:
				restaurants, self._view, err = self.primary_server.get_restaurants()
				return restaurants, err
			except Exception:
				self.primary_server = self.find_primary()
		return False, True

	@Pyro4.expose
	def get_menu(self, rest_id):
		while self.primary_server:
			try:
				menu, self._view, err = self.primary_server.get_menu(rest_id)
				return menu, err
			except Exception:
				self.primary_server = self.find_primary()
		return False, True

	@Pyro4.expose
	def add_user(self, user):
		while self.primary_server:
			try:
				user_id, self._view, err = self.primary_server.add_user(user)
				return user_id, err
			except Exception:
				self.primary_server = self.find_primary()
		return False, True

	@Pyro4.expose
	def get_user(self, user_id):
		while self.primary_server:
			try:
				user, self._view, err = self.primary_server.get_user(user_id)
				return user, err
			except Exception:
				self.primary_server = self.find_primary()
		return False, True
	
	@Pyro4.expose
	def get_user_orders(self, user_id):
		while self.primary_server:
			try:
				user_orders, self._view, err = self.primary_server.get_user_orders(user_id)
				return user_orders, err
			except Exception:
				self.primary_server = self.find_primary()
		return False, True
	
	@Pyro4.expose
	@property
	def view(self):
		return self._view

	@Pyro4.expose
	@view.setter
	def view(self, view):
		self._view = view

	def find_primary(self):
		new_primary = None 
		while not new_primary:
			self.broadcast_view()
			new_primary = Pyro4.Proxy("PYRONAME:hungry_server.primary")
			if not self._view:
				return False
		return new_primary
	
	def broadcast_view(self):
		'''Want to get list of availible servers and then broadcast to all of them a view containing them minus the current primary server'''
		if self.primary_server == "start":
			with Pyro4.locateNS() as ns:
				for server, server_uri in ns.list(prefix="hungry_server.back_up.").items():
					self._view.append(server_uri)	
				send_to = self._view
		else:
			send_to = self._view

		for server in self._view:
			try:
				server_obj = Pyro4.Proxy(server)
				server_obj.set_view(send_to)
			except:
				send_to.remove(server)
			
		
def main():
	try:
		with Pyro4.Daemon() as daemon:
			with Pyro4.locateNS() as ns:
				try:
					primary_uri = ns.lookup("hungry_server.primary")
					primary_server = Pyro4.Proxy(primary_uri)
				except:
					primary_server = "start"

			hungy_front_end = Just_Hungry(primary_server)

			hungy_front_end_uri = daemon.register(hungy_front_end)
			with Pyro4.locateNS() as ns:
				ns.register("hungry_server.front_end", hungy_front_end_uri)

			print("Front end successfully setup and running")
			daemon.requestLoop()
			ns.remove("hungry_server.front_end")
	except:
		print("No name server could be found")
	

if __name__ == "__main__":
	main()
