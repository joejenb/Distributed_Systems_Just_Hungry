'''Exaplain how to install requests library'''
import Pyro4, copy, time, json, requests
from Person import Person 
from Restaurant import Restaurant
from Database import Database 

class Hungry_Server:
	def __init__(self, data_base, rid, apis, primary_server = False):
		self._primary_server = primary_server
		self._servers = [] 
		self._db = data_base
		self._id = rid
		self._apis = apis

	@Pyro4.expose
	def new_order(self, user_id, rest_id, item_id):
		if user_id in self._db.users:
			if rest_id in self._db.restaurants:
				if item_id in range(len(self._db.restaurants[rest_id].dishes)): 
					n_key = self._db.get_key("orders")
					self._db.orders[n_key] = [user_id, rest_id, item_id]
					self._db.users[user_id].new_order(n_key)
					self._db.restaurants[rest_id].new_order(n_key)
					self.update_states("orders", {"id": n_key, "order": self._db.orders[n_key]})
					return n_key, self._servers, False
				return False, self._servers, "Invalid menu id entered"
			return False, self._servers, "Invlaid restaurant id entered"
		return False, self._servers, "Invalid user id entered"

	@Pyro4.expose
	def	get_restaurants(self):
		res = self._db.restaurants
		restaurants = {res_id: res[res_id].name for res_id in res.keys()}
		return restaurants, self._servers, False

	@Pyro4.expose
	def get_menu(self, rest_id):
		if rest_id in self._db.restaurants:
			return self._db.restaurants[rest_id].dishes, self._servers, False
		return False, self._servers, "Invalid restaurant id entered"

	@Pyro4.expose
	def add_user(self, user):
		n_key = self._db.get_key("users")
		validity, err = self.validate_postcode(user["postcode"])
		if not err:
			self._db.users[n_key] = Person(n_key, user["name"], user["postcode"]) 
			self.update_states("users", {"id": n_key, "name": user["name"], "postcode": user["postcode"]})
			return n_key, self._servers, False
		return False, self._servers, validity

	@Pyro4.expose
	def get_user(self, user_id):
		if user_id in self._db.users:
			user = self._db.users[user_id]
			return {"Name": user.name, "Postcode": user.postcode}, self._servers, False
		return False, self._servers, "Invalid user id entered" 
	
	@Pyro4.expose
	def get_user_orders(self, user_id):
		user_orders = {}
		if user_id in self._db.users:
			for order in self._db.users[user_id].orders.values():
				order_ids = self._db.orders[order]  
				restaurant = {"id": order_ids[1], "restaurant": self._db.restaurants[order_ids[1]].name}
				item = {"id": order_ids[2], "order": self._db.restaurants[order_ids[1]].dishes[order_ids[2]]}
				user_orders[order] = {"restaurant": restaurant, "order": item} 
			return user_orders, self._servers, False
		return False, self._servers, "Invalid user id entered"

	@Pyro4.expose	
	def primary_update(self, update_att, update):
		if update_att == "users":
			self._db.users[update["id"]] = Person(update["id"], update["name"], update["postcode"]) 
		elif update_att == "orders":
			self._db.orders[update["id"]] = update["order"]
			self._db.users[update["order"][0]].new_order(update["id"])
			self._db.restaurants[update["order"][1]].new_order(update["id"])
		elif update_att == "add_server":
			self._servers.append(update)
		elif update_att == "remove_server":
			self._servers.remove(update)

	@Pyro4.expose
	def set_view(self, view):
		self._servers = view
		primary = Pyro4.Proxy(self._servers.pop(0))
		if self._id == primary.id:
			self._primary_server = True
			with Pyro4.locateNS() as ns:
				server_uri = ns.lookup("hungry_server.back_up."+ str(self._id))
				ns.remove("hungry_server.back_up." + str(self._id))
				ns.register("hungry_server.primary", server_uri)

	def update_states(self, update_att, update):
		tmp_servers = self._servers.copy()
		for server in tmp_servers:
			try:
				server_obj = Pyro4.Proxy(server)
				server_obj.primary_update(update_att, update)
			except:
				self._servers.remove(server)
				self.update_view(server, False)

	@Pyro4.expose
	def update_view(self, fault_server, new_server):
		tmp_servers = self._servers.copy()
		if fault_server:
			for server in tmp_servers:
				try:
					server_obj = Pyro4.Proxy(server)
					server_obj.primary_update("remove_server", fault_server)
				except:
					self._servers.remove(server)
					self.update_view(server, False)
		elif new_server: 
			for server in tmp_servers:
				try:
					server_obj = Pyro4.Proxy(server)
					server_obj.primary_update("add_server", new_server)
				except:
					self._servers.remove(server)
					self.update_view(server, False)
			users, orders = {}, {}
			for user in self._db.users.keys():
				users[user] = {"name": self._db.users[user].name, "postcode": self._db.users[user].postcode}
			for order in self._db.orders.keys():
				orders[order] = self._db.orders[order]
			self._servers.append(new_server)
			front_end = Pyro4.Proxy("PYRONAME:hungry_server.front_end")
			front_end.view = self._servers
			return users, orders

	def validate_postcode(self, postcode):
		postcode = ''.join(postcode.split())
		postcode = postcode[:-3] + "%20" + postcode[-3:]
		for api in self._apis:
			try:
				api_res = requests.get(api+postcode, headers={'Content-Type': 'application/json'})
				txt_res = json.loads(api_res.content.decode('utf-8'))
				if txt_res["status"] == "match" or txt_res["status"] == 200:
					return False, False
				return "Invalid postcode entered", True
			except:
				print("Could not connect to:	" + api)
		return "Unable to connect to any APIs currently", True
		
	@Pyro4.expose
	@property
	def primary_server(self):
		return self._primary_server

	@Pyro4.expose
	@property
	def db(self):
		return self._db

	@Pyro4.expose
	@db.setter
	def db(self, db):
		self._db = db

	@Pyro4.expose
	@property
	def id(self):
		return self._id

def main():
	APIs = ["http://api.getthedata.com/postcode/", "http://api.postcodes.io/postcodes/"]
	data_base = Database({1: Restaurant(1, "ASK", "Italian", ["Pizza", "Pasta"]), 2: Restaurant(2, "Stantons", "British", ["Cod", "Chips"])}) 
	replica_ids = []
	
	try:
		with Pyro4.Daemon() as daemon:
			with Pyro4.locateNS() as ns:
				for server, server_uri in ns.list(prefix="hungry_server.").items():
					if server != "hungry_server.front_end":
						server = Pyro4.Proxy(server_uri)
						replica_ids.append(server.id)

				new_id = max(replica_ids) + 1 if replica_ids else 1
				server = Hungry_Server(data_base, new_id, APIs)
				server_uri = daemon.register(server)
				ns.register("hungry_server.back_up." + str(server.id), server_uri)

				try:
					primary_uri = ns.lookup("hungry_server.primary")
					primary_server = Pyro4.Proxy(primary_uri)
					try:
						users, orders = primary_server.update_view(False, server_uri)
						for user in users.keys():
							server.primary_update("users", {"id": user, "name": users[user]["name"], "postcode": users[user]["postcode"]})
						for order in orders.keys():
							server.primary_update("orders", {"id": order, "order": orders[order]})
					except:
						exit(1)
				except:
					pass

				print("Replica successfully setup and running")
				daemon.requestLoop()

				if server.primary_server:
					ns.remove("hungry_server.primary")
				else:
					ns.remove("hungry_server.back_up." + str(server.id))
	except:
		print("No name server could be found")


if __name__ == "__main__":
	main()
